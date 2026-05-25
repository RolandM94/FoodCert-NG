from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import EmployerStaffRole, InviteStatus, UserInvite, UserRole, UserStatus
from apps.accounts.services import InviteService
from apps.assessments.models import FitnessDecision, MedicalAssessment
from apps.audit.models import AuditLog
from apps.certificates.models import Certificate, CertificateStatus
from apps.employers.models import Employer, EstablishmentCategory, SubscriptionStatus as EmployerSubscriptionStatus
from apps.facilities.models import AccreditationStatus, FacilityType, MedicalFacility, OwnershipType
from apps.illness.models import ClearanceStatus, IllnessReport, SuspectedCondition
from apps.illness.services import IllnessService
from apps.inspections.models import Inspection, InspectionResponseType, InspectionStatus
from apps.locations.models import State, LGA
from apps.notifications.models import Notification, NotificationType
from apps.organizations.models import Organization, OrganizationType, OrganizationUnit, OrganizationUnitType
from apps.food_handlers.models import FoodHandlerProfile, FoodHandlerCategory, FoodHandlerStatus, Gender
from apps.payments.models import PaymentStatus, PaymentTransaction
from apps.subscriptions.models import BillingCycle, EmployerSubscription, EmployerSubscriptionPlan, SubscriptionStatus
from apps.vaccinations.models import VaccinationRecord, VaccinationStatus, VaccineType

User = get_user_model()


def data(response):
    return response.data.get("data", response.data) if isinstance(response.data, dict) else response.data


class EmployerProfileCRUDTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.lga = LGA.objects.create(name="Ikeja", state=self.state)
        self.org = Organization.objects.create(
            name="MegaChow Ltd",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        self.employer_user = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.org,
            state=self.state,
        )
        self.state_admin = User.objects.create_user(
            username="state-admin",
            email="state-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.state,
        )
        self.food_handler = User.objects.create_user(
            username="handler",
            email="handler@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
        )

    def test_employer_can_create_profile(self):
        self.client.force_authenticate(self.employer_user)
        response = self.client.post(
            "/api/employers/",
            {
                "business_name": "MegaChow",
                "business_registration_number": "RC123456",
                "establishment_category": EstablishmentCategory.RESTAURANT_CAFE,
                "contact_person_name": "John Doe",
                "contact_person_phone": "08030000000",
                "contact_person_email": "john@megachow.com",
                "address": "123 Main St",
                "state": f"{self.state.id}",
                "lga": f"{self.lga.id}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data(response)["business_name"], "MegaChow")
        self.assertEqual(f"{data(response)['state']}", f"{self.state.id}")

    def test_food_handler_cannot_create_employer_profile(self):
        self.client.force_authenticate(self.food_handler)
        response = self.client.post(
            "/api/employers/",
            {
                "business_name": "BadCo",
                "establishment_category": EstablishmentCategory.RESTAURANT_CAFE,
                "contact_person_name": "Bad",
                "contact_person_phone": "08000000000",
                "contact_person_email": "bad@bad.com",
                "address": "Bad",
                "state": f"{self.state.id}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_employer_cannot_create_duplicate_profile(self):
        self.client.force_authenticate(self.employer_user)
        self.client.post(
            "/api/employers/",
            {
                "business_name": "MegaChow",
                "establishment_category": EstablishmentCategory.RESTAURANT_CAFE,
                "contact_person_name": "John",
                "contact_person_phone": "08030000000",
                "contact_person_email": "j@a.com",
                "address": "x",
                "state": f"{self.state.id}",
            },
            format="json",
        )
        response = self.client.post(
            "/api/employers/",
            {
                "business_name": "MegaChow 2",
                "establishment_category": EstablishmentCategory.RESTAURANT_CAFE,
                "contact_person_name": "John",
                "contact_person_phone": "08030000000",
                "contact_person_email": "j2@a.com",
                "address": "y",
                "state": f"{self.state.id}",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_state_admin_can_list_employers_in_state(self):
        self.client.force_authenticate(self.employer_user)
        self.client.post(
            "/api/employers/",
            {
                "business_name": "MegaChow",
                "establishment_category": EstablishmentCategory.RESTAURANT_CAFE,
                "contact_person_name": "John",
                "contact_person_phone": "08030000000",
                "contact_person_email": "j@a.com",
                "address": "x",
                "state": f"{self.state.id}",
            },
            format="json",
        )
        self.client.force_authenticate(self.state_admin)
        response = self.client.get("/api/employers/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data(response)), 1)

    def test_employer_invite_food_handler_endpoint_creates_scoped_user(self):
        employer = Employer.objects.create(
            user=self.employer_user,
            organization=self.org,
            business_name="MegaChow",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="John",
            contact_person_phone="08030000000",
            contact_person_email="j@a.com",
            address="x",
            state=self.state,
        )
        self.client.force_authenticate(self.employer_user)

        response = self.client.post(
            f"/api/employers/{employer.id}/invite-food-handler/",
            {
                "username": "new-handler",
                "email": "new-handler@example.com",
                "password": "StrongPass123!",
                "first_name": "New",
                "last_name": "Handler",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        invited = User.objects.get(email="new-handler@example.com")
        self.assertEqual(invited.role, UserRole.FOOD_HANDLER)
        self.assertEqual(invited.organization, self.org)
        self.assertEqual(invited.state, self.state)
        self.assertTrue(AuditLog.objects.filter(target_id=str(invited.id), metadata__event="employer_food_handler_invite").exists())

    def test_employer_admin_can_invite_and_revoke_internal_user(self):
        employer = Employer.objects.create(
            user=self.employer_user,
            organization=self.org,
            business_name="MegaChow",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="John",
            contact_person_phone="08030000000",
            contact_person_email="j@a.com",
            address="x",
            state=self.state,
        )
        self.client.force_authenticate(self.employer_user)

        response = self.client.post(
            f"/api/employers/{employer.id}/invites/",
            {
                "email": "compliance@example.com",
                "phone": "08030001111",
                "employer_staff_role": "compliance_officer",
                "message": "Join compliance desk.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        payload = data(response)
        self.assertEqual(payload["role"], UserRole.EMPLOYER)
        self.assertEqual(payload["employer_staff_role"], "compliance_officer")
        self.assertEqual(UserInvite.objects.filter(email="compliance@example.com", organization=self.org).count(), 1)

        revoke_response = self.client.delete(f"/api/employers/{employer.id}/invites/{payload['id']}/")
        self.assertEqual(revoke_response.status_code, 200)
        self.assertEqual(data(revoke_response)["status"], InviteStatus.REVOKED)

    def test_employer_admin_can_invite_branch_manager_and_update_user(self):
        employer = Employer.objects.create(
            user=self.employer_user,
            organization=self.org,
            business_name="MegaChow",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="John",
            contact_person_phone="08030000000",
            contact_person_email="j@a.com",
            address="x",
            state=self.state,
        )
        branch = OrganizationUnit.objects.create(organization=self.org, name="Ikeja", unit_type=OrganizationUnitType.BRANCH)
        staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.org,
            state=self.state,
        )
        self.client.force_authenticate(self.employer_user)

        invite_response = self.client.post(
            f"/api/employers/{employer.id}/invites/",
            {"email": "branch@example.com", "employer_staff_role": "branch_manager", "unit": str(branch.id)},
            format="json",
        )
        self.assertEqual(invite_response.status_code, 201)
        self.assertEqual(str(data(invite_response)["unit"]), str(branch.id))

        update_response = self.client.patch(
            f"/api/employers/{employer.id}/users/{staff.id}/",
            {"employer_staff_role": "branch_manager", "unit": str(branch.id), "status": UserStatus.INACTIVE},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        staff.refresh_from_db()
        self.assertEqual(staff.unit, branch)
        self.assertTrue(staff.unit_restricted)
        self.assertEqual(staff.status, UserStatus.INACTIVE)

    def test_branch_manager_cannot_manage_internal_users(self):
        employer = Employer.objects.create(
            user=self.employer_user,
            organization=self.org,
            business_name="MegaChow",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="John",
            contact_person_phone="08030000000",
            contact_person_email="j@a.com",
            address="x",
            state=self.state,
        )
        branch = OrganizationUnit.objects.create(organization=self.org, name="Ikeja", unit_type=OrganizationUnitType.BRANCH)
        branch_manager = User.objects.create_user(
            username="branch-manager",
            email="branch-manager@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.org,
            unit=branch,
            unit_restricted=True,
            state=self.state,
        )
        other_staff = User.objects.create_user(
            username="other-staff",
            email="other-staff@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.org,
            state=self.state,
        )
        self.client.force_authenticate(branch_manager)

        list_response = self.client.get(f"/api/employers/{employer.id}/users/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(data(list_response)), 1)
        self.assertEqual(data(list_response)[0]["id"], str(branch_manager.id))

        invite_response = self.client.post(
            f"/api/employers/{employer.id}/invites/",
            {"email": "finance@example.com", "employer_staff_role": "finance_user"},
            format="json",
        )
        self.assertEqual(invite_response.status_code, 403)

        update_response = self.client.patch(
            f"/api/employers/{employer.id}/users/{other_staff.id}/",
            {"status": UserStatus.INACTIVE},
            format="json",
        )
        self.assertEqual(update_response.status_code, 403)


class EmployerSubscriptionBillingTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.org = Organization.objects.create(
            name="MegaChow Ltd",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        self.employer_user = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.org,
            state=self.state,
        )
        self.employer = Employer.objects.create(
            user=self.employer_user,
            organization=self.org,
            business_name="MegaChow",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="John",
            contact_person_phone="08030000000",
            contact_person_email="j@a.com",
            address="x",
            state=self.state,
        )
        self.basic = EmployerSubscriptionPlan.objects.create(
            name="Basic",
            description="Starter",
            max_food_handlers=10,
            max_locations=1,
            price_monthly="10000.00",
            price_yearly="100000.00",
            features={"handler_management": True},
        )
        self.standard = EmployerSubscriptionPlan.objects.create(
            name="Standard",
            description="Growth",
            max_food_handlers=50,
            max_locations=5,
            price_monthly="25000.00",
            price_yearly="250000.00",
            features={"branch_reports": True},
        )

    def test_subscription_checkout_activates_plan_and_returns_usage(self):
        self.client.force_authenticate(self.employer_user)

        response = self.client.post(
            f"/api/employers/{self.employer.id}/subscription/checkout/",
            {"plan_id": str(self.basic.id), "billing_cycle": BillingCycle.MONTHLY},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        payload = data(response)
        self.assertEqual(str(payload["plan"]), str(self.basic.id))
        self.assertTrue(payload["is_active"])
        self.assertEqual(payload["max_food_handlers"], 10)
        self.assertEqual(PaymentTransaction.objects.filter(status=PaymentStatus.SUCCESS).count(), 1)

    def test_change_plan_cancels_previous_subscription_and_creates_new_one(self):
        self.client.force_authenticate(self.employer_user)
        self.client.post(
            f"/api/employers/{self.employer.id}/subscription/checkout/",
            {"plan_id": str(self.basic.id), "billing_cycle": BillingCycle.MONTHLY},
            format="json",
        )

        response = self.client.patch(
            f"/api/employers/{self.employer.id}/subscription/change-plan/",
            {"plan_id": str(self.standard.id), "billing_cycle": BillingCycle.YEARLY},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(data(response)["plan"]), str(self.standard.id))
        self.assertEqual(EmployerSubscription.objects.filter(status=SubscriptionStatus.ACTIVE).count(), 1)
        self.assertEqual(EmployerSubscription.objects.filter(status=SubscriptionStatus.CANCELLED).count(), 1)

    def test_billing_history_endpoints_return_transactions_and_invoices(self):
        PaymentTransaction.objects.create(
            payer_user=self.employer_user,
            payer_type="employer",
            related_entity_type="employer_subscription",
            related_entity_id=self.employer.id,
            amount="10000.00",
            payment_provider="mock",
            provider_reference="mock-sub",
            internal_reference="SUB-BILLING-001",
            status=PaymentStatus.SUCCESS,
        )
        self.client.force_authenticate(self.employer_user)

        payments_response = self.client.get(f"/api/employers/{self.employer.id}/payments/")
        invoices_response = self.client.get(f"/api/employers/{self.employer.id}/invoices/")

        self.assertEqual(payments_response.status_code, 200)
        self.assertEqual(invoices_response.status_code, 200)
        self.assertEqual(data(payments_response)[0]["internal_reference"], "SUB-BILLING-001")
        self.assertEqual(data(invoices_response)[0]["invoice_number"], "INV-SUB-BILLING-001")


class EmployerBranchScopingTests(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.lga = LGA.objects.create(name="Ikeja", state=self.state)
        self.org = Organization.objects.create(
            name="MegaChow Ltd",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        self.hq_user = User.objects.create_user(
            username="hq",
            email="hq@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.org,
            state=self.state,
        )
        self.branch_ikeja = OrganizationUnit.objects.create(
            organization=self.org,
            name="Branch - Ikeja",
            unit_type=OrganizationUnitType.BRANCH,
            state=self.state,
            lga=self.lga,
        )
        self.branch_surulere = OrganizationUnit.objects.create(
            organization=self.org,
            name="Branch - Surulere",
            unit_type=OrganizationUnitType.BRANCH,
            state=self.state,
        )
        self.branch_manager = User.objects.create_user(
            username="ikeja-mgr",
            email="ikeja@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.org,
            state=self.state,
            unit=self.branch_ikeja,
            unit_restricted=True,
        )
        self.employer = Employer.objects.create(
            user=self.hq_user,
            organization=self.org,
            business_name="MegaChow",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="John",
            contact_person_phone="08030000000",
            contact_person_email="j@a.com",
            address="123 Main St",
            state=self.state,
        )
        self.handler_ikeja_user = User.objects.create_user(
            username="handler-ikeja",
            email="handler-ikeja@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
        )
        self.handler_surulere_user = User.objects.create_user(
            username="handler-surulere",
            email="handler-surulere@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
        )
        self.handler_ikeja = FoodHandlerProfile.objects.create(
            user=self.handler_ikeja_user,
            full_name="Ada Ikeja",
            date_of_birth="1990-01-01",
            gender=Gender.FEMALE,
            nin="12345678901",
            phone="08010000001",
            email="ada-ikeja@example.com",
            home_address="Ikeja",
            state=self.state,
            lga=self.lga,
            employer=self.employer,
            business_branch=self.branch_ikeja,
            food_handler_category=FoodHandlerCategory.KITCHEN_STAFF,
            system_identifier="FCN-IKEJA001",
        )
        self.handler_surulere = FoodHandlerProfile.objects.create(
            user=self.handler_surulere_user,
            full_name="Bola Surulere",
            date_of_birth="1992-02-02",
            gender=Gender.FEMALE,
            nin="98765432109",
            phone="08010000002",
            email="bola-surulere@example.com",
            home_address="Surulere",
            state=self.state,
            lga=self.lga,
            employer=self.employer,
            business_branch=self.branch_surulere,
            food_handler_category=FoodHandlerCategory.FOOD_PREPARER,
            system_identifier="FCN-SURU001",
        )

    def test_head_office_sees_all_branch_food_handlers(self):
        self.client.force_authenticate(self.hq_user)
        response = self.client.get("/api/food-handlers/")
        self.assertEqual(response.status_code, 200)
        results = data(response)
        self.assertEqual(len(results), 2)

    def test_branch_manager_sees_only_own_branch_food_handlers(self):
        self.client.force_authenticate(self.branch_manager)
        response = self.client.get("/api/food-handlers/")
        self.assertEqual(response.status_code, 200)
        results = data(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["full_name"], "Ada Ikeja")

    def test_food_handler_auto_inherits_branch_on_create(self):
        handler_user = User.objects.create_user(
            username="new-handler",
            email="new-handler@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            organization=self.org,
            state=self.state,
            unit=self.branch_ikeja,
        )
        self.client.force_authenticate(handler_user)
        response = self.client.post(
            "/api/food-handlers/",
            {
                "full_name": "New Handler",
                "date_of_birth": "1995-05-05",
                "gender": Gender.FEMALE,
                "nin": "11122334455",
                "phone": "08011111111",
                "email": "new-handler@example.com",
                "home_address": "Ikeja",
                "state": f"{self.state.id}",
                "lga": f"{self.lga.id}",
                "food_handler_category": FoodHandlerCategory.KITCHEN_STAFF,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(f"{data(response)['business_branch']}", f"{self.branch_ikeja.id}")

    def test_business_branch_validation_enforces_same_organization(self):
        self.client.force_authenticate(self.hq_user)
        other_org = Organization.objects.create(
            name="Other",
            organization_type=OrganizationType.EMPLOYER,
            state=self.state,
        )
        other_branch = OrganizationUnit.objects.create(
            organization=other_org,
            name="Other Branch",
            unit_type=OrganizationUnitType.BRANCH,
        )
        response = self.client.patch(
            f"/api/food-handlers/{self.handler_ikeja.id}/",
            {"business_branch": f"{other_branch.id}"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)


class EmployerE11Base(APITestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.lga = LGA.objects.create(name="Ikeja", state=self.state)
        self.org = Organization.objects.create(name="MegaChow Ltd", organization_type=OrganizationType.EMPLOYER, state=self.state, lga=self.lga)
        self.facility_org = Organization.objects.create(name="Care Clinic", organization_type=OrganizationType.MEDICAL_FACILITY, state=self.state)
        self.owner = User.objects.create_user(
            username="e11-owner",
            email="e11-owner@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.org,
            state=self.state,
        )
        self.compliance_officer = User.objects.create_user(
            username="e11-compliance",
            email="e11-compliance@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            employer_staff_role=EmployerStaffRole.COMPLIANCE_OFFICER,
            organization=self.org,
            state=self.state,
        )
        self.finance_user = User.objects.create_user(
            username="e11-finance",
            email="e11-finance@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            employer_staff_role=EmployerStaffRole.FINANCE_USER,
            organization=self.org,
            state=self.state,
        )
        self.doctor = User.objects.create_user(
            username="e11-doctor",
            email="e11-doctor@example.com",
            password="StrongPass123!",
            role=UserRole.DOCTOR,
            organization=self.facility_org,
            state=self.state,
        )
        self.inspector = User.objects.create_user(
            username="e11-inspector",
            email="e11-inspector@example.com",
            password="StrongPass123!",
            role=UserRole.INSPECTOR,
            state=self.state,
        )
        self.branch = OrganizationUnit.objects.create(organization=self.org, name="Ikeja Branch", unit_type=OrganizationUnitType.BRANCH, state=self.state, lga=self.lga)
        self.other_branch = OrganizationUnit.objects.create(organization=self.org, name="Yaba Branch", unit_type=OrganizationUnitType.BRANCH, state=self.state)
        self.branch_manager = User.objects.create_user(
            username="e11-branch",
            email="e11-branch@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            employer_staff_role=EmployerStaffRole.BRANCH_MANAGER,
            organization=self.org,
            unit=self.branch,
            unit_restricted=True,
            state=self.state,
        )
        self.employer = Employer.objects.create(
            user=self.owner,
            organization=self.org,
            business_name="MegaChow",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada",
            contact_person_phone="08030000000",
            contact_person_email="ada@megachow.test",
            address="1 Food Road",
            state=self.state,
            lga=self.lga,
        )
        self.facility = MedicalFacility.objects.create(
            organization=self.facility_org,
            facility_name="Care Clinic",
            facility_type=FacilityType.CLINIC,
            ownership_type=OwnershipType.PRIVATE,
            license_number="E11-CLINIC",
            address="1 Health Road",
            state=self.state,
            contact_person="Dr Ada",
            phone="08030000001",
            email="clinic@example.com",
            accreditation_status=AccreditationStatus.APPROVED,
            accreditation_start_date=timezone.localdate(),
            accreditation_expiry_date=timezone.localdate() + timezone.timedelta(days=90),
        )
        self.handler = self._handler("Ada Handler", "FCN-E11-001", self.branch, FoodHandlerStatus.FIT)
        self.other_handler = self._handler("Bola Handler", "FCN-E11-002", self.other_branch, FoodHandlerStatus.CERTIFICATION_PENDING)
        self.payment = PaymentTransaction.objects.create(
            payer_user=self.handler.user,
            payer_type="food_handler",
            related_entity_type="food_handler_assessment",
            related_entity_id=self.handler.id,
            amount="15000.00",
            payment_provider="mock",
            internal_reference="E11-ASSESSMENT",
            status=PaymentStatus.SUCCESS,
            paid_at=timezone.now(),
        )
        self.assessment = MedicalAssessment.objects.create(
            food_handler=self.handler,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            payment_transaction=self.payment,
            declaration_status="validated",
            physical_exam_status="completed",
            lab_status="reviewed",
            vaccination_status="reviewed",
            final_decision=FitnessDecision.FIT,
            doctor_notes="Do not expose this note",
            signed_at=timezone.now(),
            status="certificate_issued",
        )
        self.certificate = Certificate.objects.create(
            certificate_number="FCN-LA-E11-001",
            food_handler=self.handler,
            assessment=self.assessment,
            employer=self.employer,
            facility=self.facility,
            doctor=self.doctor,
            issuing_state=self.state,
            issue_date=timezone.localdate(),
            expiry_date=timezone.localdate() + timezone.timedelta(days=30),
            status=CertificateStatus.ACTIVE,
            verification_url="http://localhost/verify/FCN-LA-E11-001",
            digital_signature_hash="hash",
        )
        VaccinationRecord.objects.create(
            food_handler=self.handler,
            assessment=self.assessment,
            vaccine_type=VaccineType.TYPHOID,
            dose_number=1,
            date_administered=timezone.localdate(),
            expiry_date=timezone.localdate() + timezone.timedelta(days=365),
            status=VaccinationStatus.VALID,
            notes="Private clinical vaccination note",
            recorded_by=self.doctor,
        )
        self.inspection = Inspection.objects.create(
            inspector=self.inspector,
            employer=self.employer,
            branch=self.branch,
            status=InspectionStatus.SUBMITTED,
            findings="Keep cold chain logs updated.",
        )

    def _handler(self, name, identifier, branch, status):
        user = User.objects.create_user(
            username=identifier.lower(),
            email=f"{identifier.lower()}@example.com",
            password="StrongPass123!",
            role=UserRole.FOOD_HANDLER,
            state=self.state,
        )
        return FoodHandlerProfile.objects.create(
            user=user,
            full_name=name,
            date_of_birth="1990-01-01",
            gender=Gender.FEMALE,
            nin="12345678901",
            phone=f"080{identifier[-6:]}",
            email=f"{identifier.lower()}@example.com",
            home_address="1 Food Road",
            state=self.state,
            lga=self.lga,
            employer=self.employer,
            business_branch=branch,
            food_handler_category=FoodHandlerCategory.KITCHEN_STAFF,
            system_identifier=identifier,
            current_status=status,
        )


class EmployerE11PermissionTests(EmployerE11Base):
    def test_branch_manager_only_sees_assigned_branch_food_handlers(self):
        self.client.force_authenticate(self.branch_manager)
        response = self.client.get(f"/api/employers/{self.employer.id}/food-handlers/")

        self.assertEqual(response.status_code, 200)
        rows = data(response)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["full_name"], "Ada Handler")

    def test_branch_manager_cannot_pull_other_branch_with_query_param(self):
        self.client.force_authenticate(self.branch_manager)
        response = self.client.get(f"/api/employers/{self.employer.id}/food-handlers/?branch={self.other_branch.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data(response), [])

    def test_compliance_officer_cannot_access_billing(self):
        self.client.force_authenticate(self.compliance_officer)

        payments_response = self.client.get(f"/api/employers/{self.employer.id}/payments/")
        checkout_response = self.client.post(f"/api/employers/{self.employer.id}/subscription/checkout/", {}, format="json")

        self.assertEqual(payments_response.status_code, 403)
        self.assertEqual(checkout_response.status_code, 403)

    def test_finance_user_cannot_view_health_data(self):
        self.client.force_authenticate(self.finance_user)

        handlers_response = self.client.get(f"/api/employers/{self.employer.id}/food-handlers/")
        certificates_response = self.client.get(f"/api/employers/{self.employer.id}/certificates/")
        vaccinations_response = self.client.get(f"/api/employers/{self.employer.id}/vaccinations/")
        dashboard_response = self.client.get(f"/api/employers/{self.employer.id}/dashboard/")

        self.assertEqual(handlers_response.status_code, 403)
        self.assertEqual(certificates_response.status_code, 403)
        self.assertEqual(vaccinations_response.status_code, 403)
        self.assertEqual(dashboard_response.status_code, 403)

    def test_head_office_sees_all_branches(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(f"/api/employers/{self.employer.id}/food-handlers/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual({row["full_name"] for row in data(response)}, {"Ada Handler", "Bola Handler"})

    def test_branch_manager_certificate_endpoint_is_branch_scoped(self):
        self.client.force_authenticate(self.branch_manager)
        response = self.client.get(f"/api/employers/{self.employer.id}/certificates/")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["metrics"]["total"], 1)
        self.assertEqual(len(payload["certificates"]), 1)
        self.assertEqual(payload["certificates"][0]["food_handler_name"], "Ada Handler")

    def test_food_handler_list_supports_operational_filters(self):
        self.client.force_authenticate(self.owner)

        branch_response = self.client.get(f"/api/employers/{self.employer.id}/food-handlers/?branch={self.branch.id}")
        fitness_response = self.client.get(f"/api/employers/{self.employer.id}/food-handlers/?fitness_status=certificate_expiring_soon")
        certificate_response = self.client.get(f"/api/employers/{self.employer.id}/food-handlers/?certificate_status=active")
        expiry_response = self.client.get(f"/api/employers/{self.employer.id}/food-handlers/?expiry_window=30")

        for response in [branch_response, fitness_response, certificate_response, expiry_response]:
            self.assertEqual(response.status_code, 200)
            rows = data(response)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["full_name"], "Ada Handler")


class EmployerE11PrivacyTests(EmployerE11Base):
    sensitive_terms = [
        "12345678901",
        "Do not expose this note",
        "Private clinical vaccination note",
        "stool_result",
        "diagnosis",
        "doctor_notes",
        "declaration_answers",
        "lab_tests",
    ]

    def assert_private_terms_absent(self, payload):
        rendered = str(payload)
        for term in self.sensitive_terms:
            self.assertNotIn(term, rendered)

    def test_employer_serializer_excludes_medical_and_full_nin_fields(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(f"/api/employers/{self.employer.id}/")

        self.assertEqual(response.status_code, 200)
        self.assert_private_terms_absent(data(response))

    def test_food_handler_list_does_not_leak_medical_or_nin_data(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(f"/api/employers/{self.employer.id}/food-handlers/")

        self.assertEqual(response.status_code, 200)
        self.assert_private_terms_absent(data(response))
        self.assertNotIn("nin", data(response)[0])

    def test_certificate_endpoint_does_not_leak_medical_data(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(f"/api/employers/{self.employer.id}/certificates/")

        self.assertEqual(response.status_code, 200)
        self.assert_private_terms_absent(data(response))

    def test_certificate_detail_does_not_leak_medical_data(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(f"/api/employers/{self.employer.id}/certificates/{self.certificate.id}/")

        self.assertEqual(response.status_code, 200)
        self.assert_private_terms_absent(data(response))
        self.assertNotIn("digital_signature_hash", data(response))

    def test_employer_can_send_certificate_renewal_reminder(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(f"/api/employers/{self.employer.id}/certificates/{self.certificate.id}/send-renewal-reminder/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Notification.objects.filter(
            recipient=self.handler.user,
            notification_type=NotificationType.CERTIFICATE_RENEWAL,
        ).exists())

    def test_vaccination_endpoint_does_not_leak_clinical_notes(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(f"/api/employers/{self.employer.id}/vaccinations/")

        self.assertEqual(response.status_code, 200)
        self.assert_private_terms_absent(data(response))


class EmployerE11WorkflowTests(EmployerE11Base):
    def test_employer_registration_creates_profile_and_organization(self):
        user = User.objects.create_user(
            username="new-e11-owner",
            email="new-e11-owner@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            state=self.state,
        )
        self.client.force_authenticate(user)

        response = self.client.post(
            "/api/employers/",
            {
                "business_name": "New Foods",
                "business_registration_number": "RC-E11",
                "establishment_category": EstablishmentCategory.BAKERY,
                "contact_person_name": "New Owner",
                "contact_person_phone": "08030009999",
                "contact_person_email": "owner@newfoods.test",
                "address": "2 New Road",
                "state": str(self.state.id),
                "lga": str(self.lga.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        user.refresh_from_db()
        self.assertEqual(user.organization.name, "New Foods")
        self.assertTrue(Employer.objects.filter(user=user, organization=user.organization).exists())

    def test_food_handler_invite_creates_scoped_user(self):
        self.client.force_authenticate(self.branch_manager)

        response = self.client.post(
            f"/api/employers/{self.employer.id}/invite-food-handler/",
            {
                "username": "invited-handler",
                "email": "invited-handler@example.com",
                "first_name": "Invited",
                "last_name": "Handler",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        invited = User.objects.get(email="invited-handler@example.com")
        self.assertEqual(invited.role, UserRole.FOOD_HANDLER)
        self.assertEqual(invited.organization, self.org)
        self.assertEqual(invited.unit, self.branch)

    def test_accept_invite_assigns_food_handler_to_branch_on_profile_create(self):
        invite = InviteService.create_invite(
            actor=self.owner,
            organization=self.org,
            email="accepted-handler@example.com",
            role=UserRole.FOOD_HANDLER,
            unit=self.branch,
        )

        response = self.client.post(
            f"/api/invites/{invite.token}/accept/",
            {"username": "accepted-handler", "password": "StrongPass123!", "first_name": "Accepted"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        accepted = User.objects.get(email="accepted-handler@example.com")
        self.assertEqual(accepted.unit, self.branch)
        self.client.force_authenticate(accepted)
        profile_response = self.client.post(
            "/api/food-handlers/",
            {
                "full_name": "Accepted Handler",
                "date_of_birth": "1993-01-01",
                "gender": Gender.FEMALE,
                "nin": "10987654321",
                "phone": "08030005555",
                "email": "accepted-handler@example.com",
                "home_address": "1 Branch Road",
                "state": str(self.state.id),
                "lga": str(self.lga.id),
                "food_handler_category": FoodHandlerCategory.FOOD_PREPARER,
            },
            format="json",
        )
        self.assertEqual(profile_response.status_code, 201)
        self.assertEqual(str(data(profile_response)["business_branch"]), str(self.branch.id))

    def test_bulk_upload_validates_rows_and_creates_invites(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            f"/api/employers/{self.employer.id}/food-handlers/bulk-upload/",
            {
                "branch": str(self.branch.id),
                "rows": [
                    {"full_name": "Bulk Valid", "phone": "08030007777", "email": "bulk-valid@example.com"},
                    {"full_name": "", "phone": ""},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(len(payload["created"]), 1)
        self.assertEqual(len(payload["errors"]), 1)
        self.assertTrue(User.objects.filter(email="bulk-valid@example.com", role=UserRole.FOOD_HANDLER).exists())

    def test_illness_report_auto_excludes_handler_and_return_to_work_clears(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            f"/api/employers/{self.employer.id}/illness-reports/",
            {
                "food_handler": str(self.handler.id),
                "symptoms": {"vomiting": True},
                "suspected_condition": SuspectedCondition.GENERAL_DIARRHOEA_VOMITING,
                "notes": "Operational exclusion note",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.handler.refresh_from_db()
        self.assertEqual(self.handler.current_status, FoodHandlerStatus.TEMPORARILY_EXCLUDED)
        report = IllnessReport.objects.get(id=data(response)["id"])
        report.clearance_status = ClearanceStatus.UNDER_REVIEW
        report.earliest_return_date = timezone.localdate() - timezone.timedelta(days=1)
        report.save(update_fields=["clearance_status", "earliest_return_date", "updated_at"])
        IllnessService.clearance(report=report, doctor=self.doctor, cleared=True)
        self.handler.refresh_from_db()
        report.refresh_from_db()
        self.assertEqual(report.clearance_status, ClearanceStatus.CLEARED)
        self.assertEqual(self.handler.current_status, FoodHandlerStatus.FIT)

    def test_expired_subscription_restricts_premium_reports_but_keeps_inspection_notices(self):
        self.employer.subscription_status = EmployerSubscriptionStatus.EXPIRED
        self.employer.save(update_fields=["subscription_status", "updated_at"])
        self.client.force_authenticate(self.owner)

        report_response = self.client.get(f"/api/employers/{self.employer.id}/reports/compliance/?format=csv")
        inspections_response = self.client.get(f"/api/employers/{self.employer.id}/inspections/")

        self.assertEqual(report_response.status_code, 403)
        self.assertEqual(inspections_response.status_code, 200)
        self.assertEqual(len(data(inspections_response)), 1)

    def test_inspection_response_workflow(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            f"/api/employers/{self.employer.id}/inspections/{self.inspection.id}/responses/",
            {"response_type": InspectionResponseType.ACKNOWLEDGE, "content": "Acknowledged and assigned."},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data(response)["content"], "Acknowledged and assigned.")

    def test_dashboard_returns_branch_manager_metrics(self):
        self.client.force_authenticate(self.branch_manager)
        response = self.client.get(f"/api/employers/{self.employer.id}/dashboard/?branch={self.other_branch.id}")

        self.assertEqual(response.status_code, 200)
        payload = data(response)
        self.assertEqual(payload["scope"]["branch"], str(self.branch.id))
        self.assertEqual(payload["cards"]["total_handlers"], 1)
