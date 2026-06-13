from decimal import Decimal
import hashlib
import hmac
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import EmployerStaffRole, UserRole
from apps.assessments.models import AssessmentStatus, FitnessDecision, MedicalAssessment
from apps.certificates.models import CertificateRequest, CertificateRequestStatus
from apps.employers.models import Employer, EstablishmentCategory, SubscriptionStatus as EmployerSubscriptionStatus
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.food_handlers.models import FoodHandlerCategory, FoodHandlerProfile, Gender
from apps.locations.models import State
from apps.organizations.models import Organization, OrganizationType
from apps.payments.models import AssessmentFee, LedgerEntryType, PaymentAllocation, PaymentAllocationStatus, PaymentLedgerEntry, PaymentProvider, PaymentReconciliationRecord, PaymentStatus, PaymentTransaction, PaymentWebhookEvent, PlatformFeeSetting, Receipt, ReconciliationStatus, RefundRequest, RefundStatus, WebhookProcessingStatus
from apps.payments.services import PaymentService
from apps.settlements.models import Settlement, SettlementBatch, SettlementBatchStatus, SettlementStatus
from apps.subscriptions.models import EmployerInvoice, EmployerSubscriptionPlan, InvoiceStatus

User = get_user_model()


def data(response):
    return response.data.get("data", response.data) if hasattr(response.data, "get") else response.data


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
        self.employer_finance_user = User.objects.create_user(
            username="employer-finance",
            email="employer-finance@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
            employer_staff_role=EmployerStaffRole.FINANCE_USER,
            state=self.state,
        )
        other_employer_org = Organization.objects.create(
            name="Other Foods Ltd",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        self.other_employer_user = User.objects.create_user(
            username="other-employer",
            email="other-employer@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=other_employer_org,
            state=self.state,
        )
        self.facility_admin = User.objects.create_user(
            username="facility-admin",
            email="facility-admin@example.com",
            password="StrongPass123!",
            role=UserRole.FACILITY_ADMIN,
            organization=self.facility_org,
            state=self.state,
        )
        self.facility_doctor = User.objects.create_user(
            username="facility-doctor",
            email="facility-doctor@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
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
            amount="13000.00",
            state_fee="3000.00",
            facility_fee="10000.00",
            effective_from=timezone.localdate(),
            created_by=self.state_admin,
        )
        self.platform_fee = PlatformFeeSetting.objects.create(
            fee_code=PaymentService.ASSESSMENT_PLATFORM_FEE_CODE,
            amount="2000.00",
            effective_from=timezone.localdate(),
        )
        self.food_handler_profile = FoodHandlerProfile.objects.create(
            user=self.food_handler,
            full_name="Ada Handler",
            date_of_birth="1990-01-01",
            gender=Gender.FEMALE,
            nin="12345678901",
            phone="08030000010",
            email="handler@example.com",
            home_address="1 Food Street",
            state=self.state,
            food_handler_category=FoodHandlerCategory.KITCHEN_STAFF,
            system_identifier="FH-PAY-001",
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
                "amount": "9000.00",
                "state_fee": "2000.00",
                "facility_fee": "7000.00",
                "effective_from": str(timezone.localdate()),
                "status": "active",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data(response)["amount"], "9000.00")
        self.assertEqual(data(response)["platform_fee"], "2000.00")

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

    def test_assessment_payment_quote_initialize_verify_and_receipt(self):
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler_profile,
            facility=self.facility,
            status=AssessmentStatus.PAYMENT_PENDING,
        )
        self.client.force_authenticate(self.food_handler)

        quote_response = self.client.get(f"/api/payments/assessment/{assessment.id}/fee/")
        self.assertEqual(quote_response.status_code, 200)
        self.assertEqual(data(quote_response)["amount"], "15000.00")
        self.assertEqual(data(quote_response)["fee_schedule_id"], str(self.fee.id))

        init_response = self.client.post(f"/api/payments/assessment/{assessment.id}/initialize/")
        self.assertEqual(init_response.status_code, 201)
        payment = data(init_response)
        self.assertEqual(payment["related_entity_type"], "medical_assessment")
        self.assertEqual(payment["related_entity_id"], str(assessment.id))

        verify_response = self.client.get(f"/api/payments/verify/{payment['internal_reference']}/")
        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(data(verify_response)["status"], PaymentStatus.SUCCESS)

        assessment.refresh_from_db()
        self.assertEqual(assessment.status, AssessmentStatus.PAYMENT_CONFIRMED)
        self.assertEqual(str(assessment.payment_transaction_id), payment["id"])
        self.assertTrue(Receipt.objects.filter(payment_transaction_id=payment["id"]).exists())
        allocation = PaymentAllocation.objects.get(payment_transaction_id=payment["id"])
        self.assertEqual(allocation.assessment, assessment)
        self.assertEqual(allocation.fee_schedule, self.fee)
        self.assertEqual(allocation.facility_amount, Decimal("10000.00"))
        self.assertEqual(allocation.state_amount, Decimal("3000.00"))
        self.assertEqual(allocation.platform_amount, Decimal("2000.00"))
        self.assertEqual(PaymentLedgerEntry.objects.filter(payment_transaction_id=payment["id"]).count(), 4)

        receipt_response = self.client.get(f"/api/payments/transactions/{payment['id']}/receipt/")
        self.assertEqual(receipt_response.status_code, 200)
        self.assertEqual(data(receipt_response)["payment_reference"], payment["internal_reference"])

        second_verify = self.client.get(f"/api/payments/verify/{payment['internal_reference']}/")
        self.assertEqual(second_verify.status_code, 200)
        self.assertEqual(PaymentAllocation.objects.filter(payment_transaction_id=payment["id"]).count(), 1)
        self.assertEqual(PaymentLedgerEntry.objects.filter(payment_transaction_id=payment["id"]).count(), 4)

    def test_employer_bulk_assessment_payment_allocates_each_assessment(self):
        self.food_handler_profile.employer = self.employer
        self.food_handler_profile.save(update_fields=["employer", "updated_at"])
        second_user = User.objects.create_user(
            username="handler-two",
            email="handler-two@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.state,
        )
        second_handler = FoodHandlerProfile.objects.create(
            user=second_user,
            full_name="Bola Handler",
            date_of_birth="1992-01-01",
            gender=Gender.MALE,
            nin="12345678902",
            phone="08030000011",
            email="handler-two@example.com",
            home_address="2 Food Street",
            state=self.state,
            employer=self.employer,
            food_handler_category=FoodHandlerCategory.KITCHEN_STAFF,
            system_identifier="FH-PAY-002",
        )
        first_assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler_profile,
            employer=self.employer,
            facility=self.facility,
            status=AssessmentStatus.PAYMENT_PENDING,
        )
        second_assessment = MedicalAssessment.objects.create(
            food_handler=second_handler,
            employer=self.employer,
            facility=self.facility,
            status=AssessmentStatus.PAYMENT_PENDING,
        )
        self.client.force_authenticate(self.employer_user)

        quote_response = self.client.post(
            f"/api/payments/employers/{self.employer.id}/bulk-assessments/quote/",
            {"assessment_ids": [str(first_assessment.id), str(second_assessment.id)]},
            format="json",
        )
        init_response = self.client.post(
            f"/api/payments/employers/{self.employer.id}/bulk-assessments/initialize/",
            {"assessment_ids": [str(first_assessment.id), str(second_assessment.id)]},
            format="json",
        )

        self.assertEqual(quote_response.status_code, 200)
        self.assertEqual(data(quote_response)["amount"], "30000.00")
        self.assertEqual(len(data(quote_response)["line_items"]), 2)
        self.assertEqual(init_response.status_code, 201)
        payment = data(init_response)
        self.assertEqual(payment["amount"], "30000.00")
        self.assertEqual(payment["related_entity_type"], "employer_bulk_assessment_payment")

        verify_response = self.client.get(f"/api/payments/verify/{payment['internal_reference']}/")
        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(data(verify_response)["status"], PaymentStatus.SUCCESS)
        self.assertEqual(PaymentAllocation.objects.filter(payment_transaction_id=payment["id"]).count(), 2)
        self.assertEqual(PaymentLedgerEntry.objects.filter(payment_transaction_id=payment["id"]).count(), 8)
        receipt = Receipt.objects.get(payment_transaction_id=payment["id"])
        self.assertEqual(
            {item["assessment_id"] for item in receipt.line_items},
            {str(first_assessment.id), str(second_assessment.id)},
        )
        first_assessment.refresh_from_db()
        second_assessment.refresh_from_db()
        self.assertEqual(first_assessment.status, AssessmentStatus.PAYMENT_CONFIRMED)
        self.assertEqual(second_assessment.status, AssessmentStatus.PAYMENT_CONFIRMED)

        second_verify = self.client.get(f"/api/payments/verify/{payment['internal_reference']}/")
        self.assertEqual(second_verify.status_code, 200)
        self.assertEqual(PaymentAllocation.objects.filter(payment_transaction_id=payment["id"]).count(), 2)
        self.assertEqual(PaymentLedgerEntry.objects.filter(payment_transaction_id=payment["id"]).count(), 8)

    def test_bulk_assessment_payment_rejects_ineligible_and_other_employer_assessments(self):
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler_profile,
            employer=self.employer,
            facility=self.facility,
            status=AssessmentStatus.PAYMENT_CONFIRMED,
        )
        self.client.force_authenticate(self.employer_user)

        ineligible_response = self.client.post(
            f"/api/payments/employers/{self.employer.id}/bulk-assessments/quote/",
            {"assessment_ids": [str(assessment.id)]},
            format="json",
        )
        self.client.force_authenticate(self.other_employer_user)
        other_response = self.client.post(
            f"/api/payments/employers/{self.employer.id}/bulk-assessments/quote/",
            {"assessment_ids": [str(assessment.id)]},
            format="json",
        )

        self.assertEqual(ineligible_response.status_code, 400)
        self.assertIn(other_response.status_code, {403, 404})

    def test_ledger_entries_are_immutable(self):
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler_profile,
            facility=self.facility,
            status=AssessmentStatus.PAYMENT_PENDING,
        )
        transaction_obj = PaymentService.initiate_assessment_payment_for_assessment(
            payer_user=self.food_handler,
            assessment=assessment,
        )
        PaymentService.verify_payment(reference=transaction_obj.internal_reference, actor=self.food_handler)
        entry = PaymentLedgerEntry.objects.filter(payment_transaction=transaction_obj).first()

        entry.amount = Decimal("1.00")
        with self.assertRaises(ValueError):
            entry.save()
        with self.assertRaises(ValueError):
            entry.delete()

    def test_food_handler_can_request_refund_for_successful_payment_once(self):
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler_profile,
            facility=self.facility,
            status=AssessmentStatus.PAYMENT_PENDING,
        )
        transaction_obj = PaymentService.initiate_assessment_payment_for_assessment(
            payer_user=self.food_handler,
            assessment=assessment,
        )
        PaymentService.verify_payment(reference=transaction_obj.internal_reference, actor=self.food_handler)
        transaction_obj.refresh_from_db()
        self.client.force_authenticate(self.food_handler)

        response = self.client.post(
            f"/api/payments/transactions/{transaction_obj.id}/refund-request/",
            {"reason": "Facility unavailable"},
            format="json",
        )
        duplicate = self.client.post(
            f"/api/payments/transactions/{transaction_obj.id}/refund-request/",
            {"reason": "Duplicate request"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(duplicate.status_code, 201)
        self.assertEqual(RefundRequest.objects.filter(payment_transaction=transaction_obj).count(), 1)
        refund = RefundRequest.objects.get(payment_transaction=transaction_obj)
        self.assertEqual(refund.status, RefundStatus.REQUESTED)
        self.assertEqual(refund.amount, transaction_obj.amount)

        list_response = self.client.get(f"/api/payments/transactions/{transaction_obj.id}/refund-requests/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(data(list_response)), 1)

    def test_refund_request_requires_successful_payment(self):
        transaction_obj = PaymentTransaction.objects.create(
            payer_user=self.food_handler,
            payer_type="food_handler",
            related_entity_type="medical_assessment",
            related_entity_id=self.food_handler_profile.id,
            amount="15000.00",
            payment_provider="mock",
            internal_reference="ASS-REFUND-PENDING-001",
            status=PaymentStatus.PENDING,
        )
        self.client.force_authenticate(self.food_handler)

        response = self.client.post(
            f"/api/payments/transactions/{transaction_obj.id}/refund-request/",
            {"reason": "Changed appointment"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_admin_can_approve_and_process_partial_allocation_refund_with_reversal_ledger(self):
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler_profile,
            facility=self.facility,
            status=AssessmentStatus.PAYMENT_PENDING,
        )
        transaction_obj = PaymentService.initiate_assessment_payment_for_assessment(
            payer_user=self.food_handler,
            assessment=assessment,
        )
        PaymentService.verify_payment(reference=transaction_obj.internal_reference, actor=self.food_handler)
        allocation = PaymentAllocation.objects.get(payment_transaction=transaction_obj)
        self.client.force_authenticate(self.food_handler)

        request_response = self.client.post(
            f"/api/payments/transactions/{transaction_obj.id}/refund-request/",
            {
                "payment_allocation": str(allocation.id),
                "amount": "5000.00",
                "reason": "Duplicate booking",
            },
            format="json",
        )
        refund_id = data(request_response)["id"]
        federal_admin = User.objects.create_user(
            username="refund-admin",
            email="refund-admin@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.client.force_authenticate(federal_admin)

        approve_response = self.client.post(
            f"/api/admin/refunds/{refund_id}/approve/",
            {"notes": "Valid duplicate booking"},
            format="json",
        )
        process_response = self.client.post(f"/api/admin/refunds/{refund_id}/process/")

        self.assertEqual(request_response.status_code, 201)
        self.assertEqual(approve_response.status_code, 200)
        self.assertEqual(process_response.status_code, 200)
        self.assertEqual(data(process_response)["status"], RefundStatus.REFUNDED)
        self.assertEqual(PaymentLedgerEntry.objects.filter(payment_transaction=transaction_obj, entry_type=LedgerEntryType.REFUND).count(), 1)
        self.assertEqual(PaymentLedgerEntry.objects.filter(payment_transaction=transaction_obj, entry_type=LedgerEntryType.REVERSAL).count(), 3)
        allocation.refresh_from_db()
        transaction_obj.refresh_from_db()
        self.assertEqual(allocation.status, PaymentAllocationStatus.PARTIALLY_REFUNDED)
        self.assertEqual(transaction_obj.status, PaymentStatus.SUCCESS)
        self.assertEqual(transaction_obj.metadata["refunded_amount"], "5000.00")

    def test_chargeback_records_refund_and_holds_unpaid_settlement(self):
        settlement = self._create_settleable_not_fit_settlement("CHARGEBACK")
        federal_admin = User.objects.create_user(
            username="chargeback-admin",
            email="chargeback-admin@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.client.force_authenticate(federal_admin)

        response = self.client.post(
            "/api/payments/chargeback/",
            {
                "reference": settlement.payment_transaction.internal_reference,
                "amount": "5000.00",
                "reason": "Provider chargeback notice",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data(response)["status"], RefundStatus.APPROVED)
        settlement.refresh_from_db()
        self.assertEqual(settlement.settlement_status, SettlementStatus.HELD)

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
        webhook_event = PaymentWebhookEvent.objects.get(provider_reference=transaction_obj.internal_reference)
        self.assertTrue(webhook_event.signature_valid)
        self.assertEqual(webhook_event.processing_status, WebhookProcessingStatus.PROCESSED)

    def test_provider_webhook_event_is_idempotent(self):
        transaction_obj = PaymentTransaction.objects.create(
            payer_user=self.food_handler,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.food_handler.id,
            amount="15000.00",
            payment_provider="mock",
            internal_reference="ASS-WEBHOOK-IDEMPOTENT-001",
            status=PaymentStatus.PENDING,
        )
        payload = {
            "reference": transaction_obj.internal_reference,
            "event": "charge.success",
            "provider_reference": "mock-charge-001",
            "idempotency_key": "evt-001",
        }
        self.client.post("/api/payments/webhooks/mock/", payload, format="json")
        duplicate = self.client.post("/api/payments/webhooks/mock/", payload, format="json")

        self.assertEqual(duplicate.status_code, 200)
        self.assertEqual(PaymentWebhookEvent.objects.filter(idempotency_key="evt-001").count(), 1)
        webhook_event = PaymentWebhookEvent.objects.get(idempotency_key="evt-001")
        self.assertEqual(webhook_event.processing_status, WebhookProcessingStatus.DUPLICATE)

    def test_platform_finance_can_manage_provider_without_secret_leak(self):
        federal_admin = User.objects.create_user(
            username="finance-admin",
            email="finance-admin@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.client.force_authenticate(federal_admin)

        response = self.client.post(
            "/api/admin/payment-providers/",
            {
                "name": "Mock Provider",
                "code": "mock-configured",
                "environment": "test",
                "public_key": "pk_test",
                "encrypted_secret_key": "secret-value",
                "webhook_secret": "webhook-secret",
                "supported_methods": ["card", "bank_transfer"],
                "supports_refunds": True,
                "supports_transfers": True,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        payload = data(response)
        self.assertNotIn("encrypted_secret_key", payload)
        self.assertNotIn("webhook_secret", payload)
        self.assertTrue(payload["has_secret_key"])
        self.assertTrue(payload["has_webhook_secret"])
        self.assertTrue(PaymentProvider.objects.filter(code="mock-configured").exists())

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

    def test_payment_transaction_serializer_redacts_medical_metadata(self):
        transaction_obj = PaymentTransaction.objects.create(
            payer_user=self.food_handler,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.food_handler.id,
            amount="15000.00",
            payment_provider="mock",
            internal_reference="ASS-PRIVATE-001",
            status=PaymentStatus.SUCCESS,
            metadata={
                "facility_id": str(self.facility.id),
                "state_id": str(self.state.id),
                "lab_results": "positive",
                "doctor_notes": "private note",
                "full_nin": "12345678901",
            },
        )
        self.client.force_authenticate(self.food_handler)

        response = self.client.get(f"/api/payments/{transaction_obj.id}/")

        self.assertEqual(response.status_code, 200)
        metadata = data(response)["metadata"]
        self.assertEqual(metadata["facility_id"], str(self.facility.id))
        self.assertNotIn("lab_results", metadata)
        self.assertNotIn("doctor_notes", metadata)
        self.assertNotIn("full_nin", metadata)

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
        invoice = EmployerInvoice.objects.get(employer=self.employer)
        self.assertEqual(invoice.status, InvoiceStatus.PAID)
        self.assertEqual(invoice.amount_paid, invoice.amount_due)
        self.assertEqual(str(invoice.subscription_id), subscription["id"])
        self.assertTrue(Receipt.objects.filter(payment_transaction=invoice.payment_transaction).exists())

    def test_employer_subscription_checkout_and_billing_history(self):
        self.client.force_authenticate(self.employer_user)

        checkout_response = self.client.post(
            f"/api/employers/{self.employer.id}/subscription/checkout/",
            {"plan_id": str(self.plan.id), "billing_cycle": "yearly"},
            format="json",
        )
        current_response = self.client.get(f"/api/employers/{self.employer.id}/subscription/")
        invoices_response = self.client.get(f"/api/employers/{self.employer.id}/invoices/")
        payments_response = self.client.get(f"/api/employers/{self.employer.id}/payments/")

        self.assertEqual(checkout_response.status_code, 201)
        self.assertEqual(current_response.status_code, 200)
        self.assertEqual(data(current_response)["billing_cycle"], "yearly")
        self.assertEqual(invoices_response.status_code, 200)
        self.assertEqual(len(data(invoices_response)), 1)
        self.assertEqual(data(invoices_response)[0]["status"], InvoiceStatus.PAID)
        self.assertEqual(data(invoices_response)[0]["amount"], "200000.00")
        self.assertEqual(payments_response.status_code, 200)
        self.assertEqual(len(data(payments_response)), 1)
        self.assertEqual(data(payments_response)[0]["status"], PaymentStatus.SUCCESS)

    def test_other_employer_cannot_view_billing_history(self):
        self.client.force_authenticate(self.employer_user)
        self.client.post(
            f"/api/employers/{self.employer.id}/subscription/checkout/",
            {"plan_id": str(self.plan.id), "billing_cycle": "monthly"},
            format="json",
        )
        self.client.force_authenticate(self.other_employer_user)

        invoices_response = self.client.get(f"/api/employers/{self.employer.id}/invoices/")
        payments_response = self.client.get(f"/api/employers/{self.employer.id}/payments/")

        self.assertIn(invoices_response.status_code, {403, 404})
        self.assertIn(payments_response.status_code, {403, 404})

    def test_employer_finance_user_can_manage_own_employer_subscription(self):
        self.client.force_authenticate(self.employer_finance_user)

        response = self.client.post(
            f"/api/employers/{self.employer.id}/subscribe/",
            {"plan": str(self.plan.id), "billing_cycle": "monthly"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_other_employer_cannot_manage_subscription(self):
        self.client.force_authenticate(self.other_employer_user)

        response = self.client.post(
            f"/api/employers/{self.employer.id}/subscribe/",
            {"plan": str(self.plan.id), "billing_cycle": "monthly"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

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

    def test_finalized_not_fit_assessment_settlement_links_allocation_and_fee_schedule(self):
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler_profile,
            facility=self.facility,
            status=AssessmentStatus.PAYMENT_PENDING,
        )
        transaction_obj = PaymentService.initiate_assessment_payment_for_assessment(
            payer_user=self.food_handler,
            assessment=assessment,
        )
        PaymentService.verify_payment(reference=transaction_obj.internal_reference, actor=self.food_handler)
        assessment.status = AssessmentStatus.NOT_FIT
        assessment.final_decision = FitnessDecision.NOT_FIT
        assessment.signed_at = timezone.now()
        assessment.signed_by = self.facility_doctor
        assessment.save(update_fields=["status", "final_decision", "signed_at", "signed_by", "updated_at"])
        allocation = PaymentAllocation.objects.get(payment_transaction=transaction_obj)
        self.client.force_authenticate(self.state_admin)

        create_response = self.client.post(
            "/api/settlements/create-from-payment/",
            {"payment_transaction": str(transaction_obj.id), "assessment": str(assessment.id)},
            format="json",
        )
        duplicate_response = self.client.post(
            "/api/settlements/create-from-payment/",
            {"payment_transaction": str(transaction_obj.id), "assessment": str(assessment.id)},
            format="json",
        )

        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(duplicate_response.status_code, 201)
        self.assertEqual(Settlement.objects.filter(payment_allocation=allocation).count(), 1)
        settlement = Settlement.objects.get(payment_allocation=allocation)
        self.assertEqual(settlement.assessment, assessment)
        self.assertEqual(settlement.fee_schedule, self.fee)
        self.assertEqual(settlement.facility, self.facility)
        self.assertEqual(settlement.state, self.state)
        self.assertEqual(settlement.facility_amount, Decimal(self.fee.facility_fee))
        self.assertEqual(str(data(create_response)["payment_allocation"]), str(allocation.id))
        self.assertEqual(str(data(create_response)["fee_schedule"]), str(self.fee.id))

    def test_fit_assessment_requires_state_certificate_approval_before_settlement(self):
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler_profile,
            facility=self.facility,
            status=AssessmentStatus.PAYMENT_PENDING,
        )
        transaction_obj = PaymentService.initiate_assessment_payment_for_assessment(
            payer_user=self.food_handler,
            assessment=assessment,
        )
        PaymentService.verify_payment(reference=transaction_obj.internal_reference, actor=self.food_handler)
        assessment.status = AssessmentStatus.FIT
        assessment.final_decision = FitnessDecision.FIT
        assessment.signed_at = timezone.now()
        assessment.signed_by = self.facility_doctor
        assessment.save(update_fields=["status", "final_decision", "signed_at", "signed_by", "updated_at"])
        self.client.force_authenticate(self.state_admin)

        blocked = self.client.post(
            "/api/settlements/create-from-payment/",
            {"payment_transaction": str(transaction_obj.id), "assessment": str(assessment.id)},
            format="json",
        )
        CertificateRequest.objects.create(
            assessment=assessment,
            requested_by=self.facility_admin,
            reviewed_by=self.state_admin,
            status=CertificateRequestStatus.APPROVED,
            reviewed_at=timezone.now(),
        )
        allowed = self.client.post(
            "/api/settlements/create-from-payment/",
            {"payment_transaction": str(transaction_obj.id), "assessment": str(assessment.id)},
            format="json",
        )

        self.assertEqual(blocked.status_code, 400)
        self.assertEqual(allowed.status_code, 201)
        self.assertEqual(str(data(allowed)["assessment"]), str(assessment.id))

    def test_active_refund_request_holds_settlement(self):
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler_profile,
            facility=self.facility,
            status=AssessmentStatus.PAYMENT_PENDING,
        )
        transaction_obj = PaymentService.initiate_assessment_payment_for_assessment(
            payer_user=self.food_handler,
            assessment=assessment,
        )
        PaymentService.verify_payment(reference=transaction_obj.internal_reference, actor=self.food_handler)
        assessment.status = AssessmentStatus.NOT_FIT
        assessment.final_decision = FitnessDecision.NOT_FIT
        assessment.signed_at = timezone.now()
        assessment.signed_by = self.facility_doctor
        assessment.save(update_fields=["status", "final_decision", "signed_at", "signed_by", "updated_at"])
        RefundRequest.objects.create(
            payment_transaction=transaction_obj,
            requested_by=self.food_handler,
            amount=transaction_obj.amount,
            reason="Duplicate payment review",
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.post(
            "/api/settlements/create-from-payment/",
            {"payment_transaction": str(transaction_obj.id), "assessment": str(assessment.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def _create_settleable_not_fit_settlement(self, reference_suffix="A"):
        assessment = MedicalAssessment.objects.create(
            food_handler=self.food_handler_profile,
            facility=self.facility,
            status=AssessmentStatus.PAYMENT_PENDING,
        )
        transaction_obj = PaymentService.initiate_assessment_payment_for_assessment(
            payer_user=self.food_handler,
            assessment=assessment,
        )
        transaction_obj.internal_reference = f"ASS-SETTLE-BATCH-{reference_suffix}"
        transaction_obj.save(update_fields=["internal_reference", "updated_at"])
        PaymentService.verify_payment(reference=transaction_obj.internal_reference, actor=self.food_handler)
        assessment.status = AssessmentStatus.NOT_FIT
        assessment.final_decision = FitnessDecision.NOT_FIT
        assessment.signed_at = timezone.now()
        assessment.signed_by = self.facility_doctor
        assessment.save(update_fields=["status", "final_decision", "signed_at", "signed_by", "updated_at"])
        return Settlement.objects.create(
            facility=self.facility,
            state=self.state,
            payment_transaction=transaction_obj,
            payment_allocation=PaymentAllocation.objects.get(payment_transaction=transaction_obj),
            fee_schedule=self.fee,
            assessment=assessment,
            gross_amount=self.fee.amount + self.platform_fee.amount,
            facility_amount=self.fee.facility_fee,
            state_amount=self.fee.state_fee,
            platform_amount=self.platform_fee.amount,
        )

    def test_settlement_batch_failure_retry_and_processing_are_guarded(self):
        settlement_one = self._create_settleable_not_fit_settlement("ONE")
        settlement_two = self._create_settleable_not_fit_settlement("TWO")
        self.client.force_authenticate(self.state_admin)

        denied = self.client.post(
            "/api/admin/settlement-batches/create/",
            {"settlements": [str(settlement_one.id)]},
            format="json",
        )
        self.assertEqual(denied.status_code, 403)

        federal_admin = User.objects.create_user(
            username="federal-finance",
            email="federal-finance@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        self.client.force_authenticate(federal_admin)
        create_response = self.client.post(
            "/api/admin/settlement-batches/create/",
            {"settlements": [str(settlement_one.id), str(settlement_two.id)]},
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(data(create_response)["settlement_count"], 2)
        self.assertEqual(data(create_response)["facility_amount"], "20000.00")
        batch = SettlementBatch.objects.get(id=data(create_response)["id"])

        approve_response = self.client.post(f"/api/admin/settlement-batches/{batch.id}/approve/")
        fail_response = self.client.post(
            f"/api/admin/settlement-batches/{batch.id}/process/",
            {"simulate_failure": True, "failure_reason": "Bank transfer timeout"},
            format="json",
        )
        self.assertEqual(approve_response.status_code, 200)
        self.assertEqual(fail_response.status_code, 200)
        batch.refresh_from_db()
        self.assertEqual(batch.status, SettlementBatchStatus.FAILED)
        self.assertEqual(Settlement.objects.filter(batch=batch, settlement_status=SettlementStatus.FAILED).count(), 2)

        retry_response = self.client.post(f"/api/admin/settlement-batches/{batch.id}/retry/")
        process_response = self.client.post(f"/api/admin/settlement-batches/{batch.id}/process/", {}, format="json")
        self.assertEqual(retry_response.status_code, 200)
        self.assertEqual(process_response.status_code, 200)
        batch.refresh_from_db()
        self.assertEqual(batch.status, SettlementBatchStatus.PAID)
        self.assertTrue(batch.payout_reference)
        self.assertEqual(Settlement.objects.filter(batch=batch, settlement_status=SettlementStatus.PAID).count(), 2)

        second_process = self.client.post(f"/api/admin/settlement-batches/{batch.id}/process/", {}, format="json")
        self.assertEqual(second_process.status_code, 400)

    def test_settlement_hold_release_and_individual_retry_flow(self):
        settlement = self._create_settleable_not_fit_settlement("HOLD")
        self.client.force_authenticate(self.state_admin)

        hold_response = self.client.post(
            f"/api/settlements/{settlement.id}/hold/",
            {"reason": "Awaiting reconciliation document"},
            format="json",
        )
        blocked_process = self.client.post(f"/api/settlements/{settlement.id}/process/")
        release_response = self.client.post(f"/api/settlements/{settlement.id}/release/")
        failed = Settlement.objects.get(id=settlement.id)
        failed.settlement_status = SettlementStatus.FAILED
        failed.last_payout_error = "Provider unavailable"
        failed.save(update_fields=["settlement_status", "last_payout_error", "updated_at"])
        retry_response = self.client.post(f"/api/settlements/{settlement.id}/retry/")

        self.assertEqual(hold_response.status_code, 200)
        self.assertEqual(data(hold_response)["settlement_status"], SettlementStatus.HELD)
        self.assertEqual(blocked_process.status_code, 400)
        self.assertEqual(release_response.status_code, 200)
        self.assertEqual(data(release_response)["settlement_status"], SettlementStatus.PENDING)
        self.assertEqual(retry_response.status_code, 200)
        self.assertEqual(data(retry_response)["settlement_status"], SettlementStatus.PENDING)

    def test_clinical_facility_staff_cannot_read_finance_settlements(self):
        transaction_obj = PaymentTransaction.objects.create(
            payer_user=self.food_handler,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.food_handler.id,
            amount="15000.00",
            payment_provider="mock",
            provider_reference="mock-assessment",
            internal_reference="ASS-FINANCE-SCOPE-001",
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
        Settlement.objects.create(
            facility=self.facility,
            state=self.state,
            payment_transaction=transaction_obj,
            gross_amount="15000.00",
            facility_amount="10000.00",
            state_amount="3000.00",
            platform_amount="2000.00",
        )

        self.client.force_authenticate(self.facility_doctor)
        blocked = self.client.get(f"/api/facilities/{self.facility.id}/settlements/")
        self.assertEqual(blocked.status_code, 403)

        self.client.force_authenticate(self.facility_admin)
        allowed = self.client.get(f"/api/facilities/{self.facility.id}/settlements/")
        self.assertEqual(allowed.status_code, 200)

    def test_payment_reconciliation_import_flags_mismatches_and_performance(self):
        federal_admin = User.objects.create_user(
            username="recon-admin",
            email="recon-admin@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        transaction_obj = PaymentTransaction.objects.create(
            payer_user=self.food_handler,
            payer_type="food_handler",
            related_entity_type="medical_assessment",
            related_entity_id=self.food_handler_profile.id,
            amount="15000.00",
            currency="NGN",
            payment_provider="paystack",
            provider_reference="PSK-MATCH-001",
            internal_reference="ASS-RECON-001",
            status=PaymentStatus.SUCCESS,
            paid_at=timezone.now(),
            metadata={"state_id": str(self.state.id), "facility_id": str(self.facility.id)},
        )
        self.client.force_authenticate(federal_admin)

        response = self.client.post(
            "/api/admin/payment-reconciliations/import/",
            {
                "provider_code": "paystack",
                "records": [
                    {
                        "provider_reference": "PSK-MATCH-001",
                        "internal_reference": transaction_obj.internal_reference,
                        "amount": "15000.00",
                        "currency": "NGN",
                        "provider_payload": {"state_id": str(self.state.id)},
                    },
                    {
                        "provider_reference": "PSK-AMOUNT-001",
                        "internal_reference": transaction_obj.internal_reference,
                        "amount": "14900.00",
                        "currency": "NGN",
                    },
                    {
                        "provider_reference": "PSK-MISSING-001",
                        "internal_reference": "ASS-NOT-FOUND",
                        "amount": "15000.00",
                        "currency": "NGN",
                    },
                    {
                        "provider_reference": "PSK-MATCH-001",
                        "internal_reference": transaction_obj.internal_reference,
                        "amount": "15000.00",
                        "currency": "NGN",
                    },
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        statuses = [item["status"] for item in data(response)]
        self.assertEqual(
            statuses,
            [
                ReconciliationStatus.MATCHED,
                ReconciliationStatus.AMOUNT_MISMATCH,
                ReconciliationStatus.MISSING_INTERNAL,
                ReconciliationStatus.DUPLICATE_PROVIDER_REFERENCE,
            ],
        )

        performance = self.client.get("/api/admin/payment-reconciliations/provider-performance/")
        self.assertEqual(performance.status_code, 200)
        self.assertEqual(data(performance)[0]["provider_code"], "paystack")
        self.assertEqual(data(performance)[0]["total_records"], 4)
        self.assertEqual(data(performance)[0]["matched_records"], 1)
        self.assertEqual(data(performance)[0]["issue_records"], 3)

    def test_payment_reconciliation_resolution_requires_notes_and_state_scope(self):
        other_state = State.objects.create(name="Oyo", code="OY")
        federal_admin = User.objects.create_user(
            username="resolve-admin",
            email="resolve-admin@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
        )
        same_state_payment = PaymentTransaction.objects.create(
            payer_user=self.food_handler,
            payer_type="food_handler",
            related_entity_type="medical_assessment",
            related_entity_id=self.food_handler_profile.id,
            amount="15000.00",
            currency="NGN",
            payment_provider="paystack",
            provider_reference="PSK-SCOPE-001",
            internal_reference="ASS-RECON-SCOPE-001",
            status=PaymentStatus.SUCCESS,
            paid_at=timezone.now(),
            metadata={"state_id": str(self.state.id), "facility_id": str(self.facility.id)},
        )
        other_payment = PaymentTransaction.objects.create(
            payer_user=self.food_handler,
            payer_type="food_handler",
            related_entity_type="medical_assessment",
            related_entity_id=self.food_handler_profile.id,
            amount="15000.00",
            currency="NGN",
            payment_provider="paystack",
            provider_reference="PSK-SCOPE-002",
            internal_reference="ASS-RECON-SCOPE-002",
            status=PaymentStatus.SUCCESS,
            paid_at=timezone.now(),
            metadata={"state_id": str(other_state.id)},
        )
        same_record = PaymentReconciliationRecord.objects.create(
            provider_code="paystack",
            provider_reference="PSK-SCOPE-001",
            internal_reference=same_state_payment.internal_reference,
            payment_transaction=same_state_payment,
            amount="14000.00",
            currency="NGN",
            status=ReconciliationStatus.AMOUNT_MISMATCH,
        )
        PaymentReconciliationRecord.objects.create(
            provider_code="paystack",
            provider_reference="PSK-SCOPE-002",
            internal_reference=other_payment.internal_reference,
            payment_transaction=other_payment,
            amount="15000.00",
            currency="NGN",
            status=ReconciliationStatus.MATCHED,
        )
        PaymentReconciliationRecord.objects.create(
            provider_code="paystack",
            provider_reference="PSK-SCOPE-003",
            internal_reference="ASS-RECON-MISSING",
            amount="15000.00",
            currency="NGN",
            status=ReconciliationStatus.MISSING_INTERNAL,
            provider_payload={"state_id": str(self.state.id)},
        )
        self.client.force_authenticate(federal_admin)

        missing_notes = self.client.post(
            f"/api/admin/payment-reconciliations/{same_record.id}/resolve/",
            {"notes": ""},
            format="json",
        )
        resolved = self.client.post(
            f"/api/admin/payment-reconciliations/{same_record.id}/resolve/",
            {"notes": "Provider statement confirms settled amount after bank fee reversal."},
            format="json",
        )

        self.assertEqual(missing_notes.status_code, 400)
        self.assertEqual(resolved.status_code, 200)
        same_record.refresh_from_db()
        self.assertEqual(same_record.status, ReconciliationStatus.MANUALLY_RESOLVED)
        self.assertEqual(same_record.resolved_by, federal_admin)

        self.client.force_authenticate(self.state_admin)
        scoped = self.client.get("/api/state/finance/reconciliation/")
        self.assertEqual(scoped.status_code, 200)
        references = {item["provider_reference"] for item in data(scoped)}
        self.assertEqual(references, {"PSK-SCOPE-001", "PSK-SCOPE-003"})
