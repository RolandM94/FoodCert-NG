from decimal import Decimal
import hashlib
import hmac
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.employers.models import Employer, EstablishmentCategory, SubscriptionStatus as EmployerSubscriptionStatus
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.locations.models import State
from apps.organizations.models import Organization, OrganizationType
from apps.payments.models import AssessmentFee, PaymentStatus, PaymentTransaction
from apps.payments.services import PaymentService
from apps.settlements.models import Settlement, SettlementStatus
from apps.subscriptions.models import EmployerSubscriptionPlan

User = get_user_model()


def data(response):
    return response.data.get("data", response.data)


class PaymentSubscriptionSettlementTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.facility_org = Organization.objects.create(
            name="Mainland Diagnostics",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=self.state,
        )
        self.employer_org = Organization.objects.create(
            name="Clean Foods Ltd",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        self.food_handler = User.objects.create_user(
            username="handler",
            email="handler@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.state,
        )
        self.state_admin = User.objects.create_user(
            username="state-admin",
            email="state-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.state,
        )
        self.employer_user = User.objects.create_user(
            username="employer",
            email="employer@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            state=self.state,
        )
        self.facility = MedicalFacility.objects.create(
            organization=self.facility_org,
            facility_name="Mainland Diagnostics",
            facility_type=FacilityType.DIAGNOSTIC_CENTRE,
            ownership_type=OwnershipType.PRIVATE,
            license_number="MD-001",
            address="12 Health Road",
            state=self.state,
            contact_person="Dr Ada",
            phone="08030000000",
            email="facility@example.com",
            accreditation_status=AccreditationStatus.APPROVED,
            accreditation_start_date=timezone.localdate(),
            accreditation_expiry_date=timezone.localdate() + timezone.timedelta(days=365),
        )
        self.inactive_facility = MedicalFacility.objects.create(
            organization=Organization.objects.create(
                name="Draft Clinic",
                organization_type=OrganizationType.MEDICAL_FACILITY,
                state=self.state,
            ),
            facility_name="Draft Clinic",
            facility_type=FacilityType.DIAGNOSTIC_CENTRE,
            ownership_type=OwnershipType.PRIVATE,
            license_number="DC-001",
            address="10 Pending Road",
            state=self.state,
            contact_person="Dr Ben",
            phone="08030000001",
            email="draft@example.com",
        )
        self.fee = AssessmentFee.objects.create(
            state=self.state,
            facility_type=FacilityType.DIAGNOSTIC_CENTRE,
            amount="15000.00",
            state_fee="3000.00",
            facility_fee="10000.00",
            platform_fee="2000.00",
            effective_from=timezone.localdate(),
            created_by=self.state_admin,
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            organization=self.employer_org,
            business_name="Clean Foods Ltd",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada Okafor",
            contact_person_phone="08030000002",
            contact_person_email="ops@cleanfoods.example",
            address="3 Market Road",
            state=self.state,
        )
        self.plan = EmployerSubscriptionPlan.objects.create(
            name="Standard",
            description="Growing food businesses",
            max_food_handlers=50,
            max_locations=5,
            price_monthly="20000.00",
            price_yearly="200000.00",
            features={"advanced_reporting": True},
        )

    def test_state_admin_creates_assessment_fee_with_server_validated_split(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            "/api/assessment-fees/",
            {
                "state": str(self.state.id),
                "facility_type": FacilityType.CLINIC,
                "amount": "10000.00",
                "state_fee": "2000.00",
                "facility_fee": "7000.00",
                "platform_fee": "1000.00",
                "effective_from": str(timezone.localdate()),
                "status": "active",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data(response)["amount"], "10000.00")

    def test_assessment_payment_requires_approved_facility(self):
        self.client.force_authenticate(self.food_handler)

        response = self.client.post(
            "/api/payments/assessment/initiate/",
            {"facility": str(self.inactive_facility.id), "food_handler_id": str(self.food_handler.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_assessment_payment_uses_configured_fee_and_verifies(self):
        self.client.force_authenticate(self.food_handler)

        response = self.client.post(
            "/api/payments/assessment/initiate/",
            {"facility": str(self.facility.id), "food_handler_id": str(self.food_handler.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        payment = data(response)
        self.assertEqual(payment["amount"], "15000.00")
        self.assertEqual(payment["status"], PaymentStatus.PENDING)
        self.assertIn("authorization_url", payment["metadata"])

        verify_response = self.client.get(f"/api/payments/verify/{payment['internal_reference']}/")

        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(data(verify_response)["status"], PaymentStatus.SUCCESS)
        self.assertIsNotNone(PaymentTransaction.objects.get(id=payment["id"]).paid_at)

    def test_payment_webhook_requires_signature_when_secret_configured(self):
        transaction_obj = PaymentTransaction.objects.create(
            payer_user=self.food_handler,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.food_handler.id,
            amount="15000.00",
            payment_provider="mock",
            internal_reference="ASS-WEBHOOK-001",
            status=PaymentStatus.PENDING,
        )
        body = {"reference": transaction_obj.internal_reference, "event": "charge.success"}

        with override_settings(PAYMENT_WEBHOOK_SECRET="secret"):
            blocked = self.client.post("/api/payments/webhook/", body, format="json")
            self.assertEqual(blocked.status_code, 403)

            raw = b'{"reference":"ASS-WEBHOOK-001","event":"charge.success"}'
            signature = hmac.new(b"secret", raw, hashlib.sha256).hexdigest()
            accepted = self.client.generic(
                "POST",
                "/api/payments/webhook/",
                raw,
                content_type="application/json",
                HTTP_X_FOODCERT_SIGNATURE=signature,
            )

        self.assertEqual(accepted.status_code, 200)
        transaction_obj.refresh_from_db()
        self.assertEqual(transaction_obj.status, PaymentStatus.SUCCESS)

    def test_successful_payment_verification_is_idempotent(self):
        transaction_obj = PaymentTransaction.objects.create(
            payer_user=self.food_handler,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.food_handler.id,
            amount="15000.00",
            payment_provider="mock",
            provider_reference="mock-existing",
            internal_reference="ASS-IDEMPOTENT-001",
            status=PaymentStatus.SUCCESS,
            paid_at=timezone.now(),
        )

        with patch("apps.payments.services.get_payment_provider") as mocked_provider:
            verified = PaymentService.verify_payment(reference=transaction_obj.internal_reference)

        self.assertEqual(verified.status, PaymentStatus.SUCCESS)
        mocked_provider.assert_not_called()

    def test_employer_can_subscribe_to_plan(self):
        self.client.force_authenticate(self.employer_user)

        response = self.client.post(
            f"/api/employers/{self.employer.id}/subscribe/",
            {"plan": str(self.plan.id), "billing_cycle": "monthly"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        subscription = data(response)
        self.assertEqual(str(subscription["plan"]), str(self.plan.id))
        self.assertTrue(subscription["is_active"])
        self.employer.refresh_from_db()
        self.assertEqual(self.employer.subscription_status, EmployerSubscriptionStatus.ACTIVE)

    def test_successful_assessment_payment_can_create_and_process_settlement(self):
        transaction_obj = PaymentTransaction.objects.create(
            payer_user=self.food_handler,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.food_handler.id,
            amount="15000.00",
            payment_provider="mock",
            provider_reference="mock-assessment",
            internal_reference="ASS-TEST-001",
            status=PaymentStatus.SUCCESS,
            paid_at=timezone.now(),
            metadata={
                "facility_id": str(self.facility.id),
                "state_id": str(self.state.id),
                "assessment_fee_id": str(self.fee.id),
                "state_fee": "3000.00",
                "facility_fee": "10000.00",
                "platform_fee": "2000.00",
            },
        )
        self.client.force_authenticate(self.state_admin)

        create_response = self.client.post(
            "/api/settlements/create-from-payment/",
            {"payment_transaction": str(transaction_obj.id)},
            format="json",
        )

        self.assertEqual(create_response.status_code, 201)
        settlement = Settlement.objects.get(id=data(create_response)["id"])
        self.assertEqual(settlement.facility_amount, Decimal(self.fee.facility_fee))
        self.assertEqual(settlement.settlement_status, SettlementStatus.PENDING)

        process_response = self.client.post(f"/api/settlements/{settlement.id}/process/")

        self.assertEqual(process_response.status_code, 200)
        settlement.refresh_from_db()
        self.assertEqual(settlement.settlement_status, SettlementStatus.PAID)
        self.assertTrue(settlement.settlement_reference)
