"""
Seed demo accounts and data for FoodCert NG presentation.

Usage:
    python manage.py seed_demo
    python manage.py seed_demo --clear

All demo passwords: Demo@2024!
"""

from datetime import date, datetime, timedelta
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import qrcode
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

User = get_user_model()

DEMO_PASSWORD = "Demo@2024!"


def _make_user(*, username, email, role, org=None, unit=None, state=None, unit_restricted=False, first_name="", last_name=""):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
            "organization": org,
            "unit": unit,
            "state": state,
            "unit_restricted": unit_restricted,
            "is_active": True,
        },
    )
    if created:
        user.set_password(DEMO_PASSWORD)
        user.save(update_fields=["password"])
    return user, created


def _make_profile(Model, defaults, **lookup):
    obj, created = Model.objects.get_or_create(**lookup, defaults=defaults)
    return obj, created


class Command(BaseCommand):
    help = "Seed FoodCert NG demo accounts and data."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Delete all demo data before seeding.")

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_demo_data()

        created_count = 0

        # ── locations ──
        from apps.locations.models import State, LGA

        lagos, _ = State.objects.get_or_create(name="Lagos", code="LA")
        fct, _ = State.objects.get_or_create(name="FCT", code="FC")
        ikeja, _ = LGA.objects.get_or_create(name="Ikeja", state=lagos)
        surulere, _ = LGA.objects.get_or_create(name="Surulere", state=lagos)

        # ── policy ──
        from apps.policy.models import StatePolicyConfig

        StatePolicyConfig.objects.get_or_create(
            state=lagos,
            defaults={
                "requires_state_certificate_validation": False,
                "certificate_validity_months": 6,
                "typhoid_validity_years": 3,
                "hepatitis_a_second_dose_months": 6,
            },
        )

        # ── organizations ──
        from apps.organizations.models import Organization, OrganizationType, OrganizationUnit, OrganizationUnitType
        from apps.accounts.models import UserRole
        from apps.food_handlers.models import FoodHandlerProfile, FoodHandlerCategory, FoodHandlerStatus, Gender

        lagos_moh, _ = Organization.objects.get_or_create(
            name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos
        )
        fed_moh, _ = Organization.objects.get_or_create(
            name="Federal MOH", organization_type=OrganizationType.FEDERAL_MINISTRY
        )
        excel_diag, _ = Organization.objects.get_or_create(
            name="Excel Diagnostics Ltd",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=lagos,
            lga=ikeja,
            address="12 Allen Avenue, Ikeja, Lagos",
        )
        prime_health, _ = Organization.objects.get_or_create(
            name="Prime Health Clinic",
            organization_type=OrganizationType.MEDICAL_FACILITY,
            state=lagos,
            lga=surulere,
            address="45 Broad Street, Surulere, Lagos",
        )
        megachow_org, _ = Organization.objects.get_or_create(
            name="MegaChow Ltd",
            organization_type=OrganizationType.EMPLOYER,
            state=lagos,
            address="Plot 15, Victoria Island, Lagos",
        )

        # ── organization units ──
        def _unit(org, name, utype, parent=None, **kw):
            return OrganizationUnit.objects.get_or_create(
                organization=org, name=name,
                defaults={"unit_type": utype, "parent": parent, **kw},
            )[0]

        fs_directorate = _unit(lagos_moh, "Food Safety Directorate", OrganizationUnitType.DIRECTORATE)
        verif_desk = _unit(lagos_moh, "Verification Desk", OrganizationUnitType.UNIT, fs_directorate)
        accred_unit = _unit(lagos_moh, "Accreditation Unit", OrganizationUnitType.UNIT, fs_directorate)
        inspectorate = _unit(lagos_moh, "Inspectorate", OrganizationUnitType.DEPARTMENT, fs_directorate)
        ikeja_lga_off = _unit(lagos_moh, "Ikeja LGA Office", OrganizationUnitType.LGA_OFFICE, inspectorate, lga=ikeja)

        excel_clinical = _unit(excel_diag, "Clinical Assessment Dept", OrganizationUnitType.CLINICAL_DEPARTMENT)
        excel_lab = _unit(excel_diag, "Laboratory Dept", OrganizationUnitType.LAB_DEPARTMENT)
        _unit(excel_diag, "Medical Records Dept", OrganizationUnitType.RECORDS_DEPARTMENT)

        mega_hq = _unit(megachow_org, "Headquarters", OrganizationUnitType.HEADQUARTERS)
        mega_ikeja = _unit(megachow_org, "Branch - Ikeja", OrganizationUnitType.BRANCH, lga=ikeja)
        mega_surulere = _unit(megachow_org, "Branch - Surulere", OrganizationUnitType.BRANCH, lga=surulere)

        # ── users ──
        users = {}

        def _u(username, email, role, org=None, unit=None, state_=None, ur=False, fn="", ln=""):
            u, cr = _make_user(username=username, email=email, role=role, org=org, unit=unit, state=state_, unit_restricted=ur, first_name=fn, last_name=ln)
            users[username] = u
            if cr:
                nonlocal created_count
                created_count += 1
            return u

        _u("super.admin", "super@foodcert.ng", UserRole.SUPER_ADMIN, fn="Super", ln="Admin")
        _u("federal.admin", "federal@foodcert.ng", UserRole.FEDERAL_ADMIN, org=fed_moh, fn="Federal", ln="Admin")

        la_state = _u("lagos.admin", "lagos-admin@foodcert.ng", UserRole.STATE_ADMIN, org=lagos_moh, state_=lagos, fn="Funke", ln="Adesina")
        _u("lagos.verifier", "verifier@foodcert.ng", UserRole.STATE_ADMIN, org=lagos_moh, unit=verif_desk, state_=lagos, fn="Tunde", ln="Balogun")
        _u("lagos.accreditor", "accreditor@foodcert.ng", UserRole.STATE_ADMIN, org=lagos_moh, unit=accred_unit, state_=lagos, fn="Ngozi", ln="Okonkwo")
        _u("lagos.inspector", "inspector@foodcert.ng", UserRole.INSPECTOR, unit=ikeja_lga_off, state_=lagos, fn="Yusuf", ln="Ibrahim")

        _u("excel.admin", "excel-admin@foodcert.ng", UserRole.FACILITY_ADMIN, org=excel_diag, state_=lagos, fn="Dr. Chidi", ln="Obi")
        excel_doc = _u("excel.doctor", "excel-doctor@foodcert.ng", UserRole.DOCTOR, org=excel_diag, unit=excel_clinical, state_=lagos, fn="Dr. Amina", ln="Bello")
        _u("excel.lab", "excel-lab@foodcert.ng", UserRole.LAB_STAFF, org=excel_diag, unit=excel_lab, state_=lagos, fn="Samuel", ln="Okafor")

        _u("prime.admin", "prime-admin@foodcert.ng", UserRole.FACILITY_ADMIN, org=prime_health, state_=lagos, fn="Dr. Fatima", ln="Yusuf")

        mega_hq_u = _u("megachow.hq", "hq@megachow.ng", UserRole.EMPLOYER, org=megachow_org, unit=mega_hq, state_=lagos, fn="Richard", ln="Cole")
        _u("megachow.ikeja", "ikeja@megachow.ng", UserRole.EMPLOYER, org=megachow_org, unit=mega_ikeja, state_=lagos, ur=True, fn="Blessing", ln="Eze")
        _u("megachow.surulere", "surulere@megachow.ng", UserRole.EMPLOYER, org=megachow_org, unit=mega_surulere, state_=lagos, ur=True, fn="David", ln="Akpan")

        # ── employer profile ──
        from apps.employers.models import Employer, EstablishmentCategory, ComplianceStatus, SubscriptionStatus

        mega_emp, _ = Employer.objects.get_or_create(
            user=mega_hq_u,
            defaults={
                "organization": megachow_org,
                "business_name": "MegaChow Ltd",
                "business_registration_number": "RC987654",
                "establishment_category": EstablishmentCategory.RESTAURANT_CAFE,
                "contact_person_name": "Richard Cole",
                "contact_person_phone": "08090000000",
                "contact_person_email": "hq@megachow.ng",
                "address": "Plot 15, Victoria Island, Lagos",
                "state": lagos,
                "lga": ikeja,
                "compliance_status": ComplianceStatus.COMPLIANT,
                "subscription_status": SubscriptionStatus.ACTIVE,
                "number_of_food_handlers": 4,
            },
        )

        # ── medical facilities ──
        from apps.facilities.models import MedicalFacility, FacilityType, OwnershipType, AccreditationStatus
        from apps.facilities.models import FacilityAccreditationApplication

        excel_fac, _ = MedicalFacility.objects.get_or_create(
            organization=excel_diag,
            defaults={
                "facility_name": "Excel Diagnostics Ltd",
                "facility_type": FacilityType.DIAGNOSTIC_CENTRE,
                "ownership_type": OwnershipType.PRIVATE,
                "license_number": "MDCN/LA/2024/001",
                "address": "12 Allen Avenue, Ikeja, Lagos",
                "state": lagos,
                "lga": ikeja,
                "accreditation_status": AccreditationStatus.APPROVED,
                "accreditation_start_date": date.today() - timedelta(days=180),
                "accreditation_expiry_date": date.today() + timedelta(days=185),
                "approved_by": la_state,
                "standard_assessment_price": "5000.00",
            },
        )
        FacilityAccreditationApplication.objects.get_or_create(
            facility=excel_fac,
            defaults={
                "application_status": "approved",
                "has_reporting_policy": True,
                "has_medical_records_computers": True,
                "has_computer_operators": True,
                "has_standard_forms": True,
                "has_patient_files": True,
                "has_qr_certificate_capability": True,
                "has_internet_access": True,
                "has_trained_records_staff": True,
                "has_trained_clinical_staff": True,
                "has_trained_non_clinical_staff": True,
                "reviewer": la_state,
            },
        )

        prime_fac, _ = MedicalFacility.objects.get_or_create(
            organization=prime_health,
            defaults={
                "facility_name": "Prime Health Clinic",
                "facility_type": FacilityType.CLINIC,
                "ownership_type": OwnershipType.PRIVATE,
                "license_number": "MDCN/LA/2024/089",
                "address": "45 Broad Street, Surulere, Lagos",
                "state": lagos,
                "lga": surulere,
                "accreditation_status": AccreditationStatus.SUBMITTED,
                "standard_assessment_price": "4000.00",
            },
        )

        # ── food handlers ──
        ada_user = _u("ada.okafor", "ada.okafor@example.com", UserRole.FOOD_HANDLER, fn="Ada", ln="Okafor")
        bola_user = _u("bola.surulere", "bola.surulere@example.com", UserRole.FOOD_HANDLER, fn="Bola", ln="Surulere")
        emeka_user = _u("emeka.nnamdi", "emeka.nnamdi@example.com", UserRole.FOOD_HANDLER, fn="Emeka", ln="Nnamdi")
        chioma_user = _u("chioma.eze", "chioma.eze@example.com", UserRole.FOOD_HANDLER, fn="Chioma", ln="Eze")

        def _fh(user, full_name, dob, gender, nin, phone, email, home_addr, lga_obj, work_loc, category, emp, branch=None, status=FoodHandlerStatus.FIT, sid=None):
            sid = sid or f"FCN-{uuid4().hex[:10].upper()}"
            obj, _ = FoodHandlerProfile.objects.get_or_create(
                user=user,
                defaults={
                    "full_name": full_name,
                    "date_of_birth": dob,
                    "gender": gender,
                    "nin": nin,
                    "phone": phone,
                    "email": email,
                    "home_address": home_addr,
                    "state": lagos,
                    "lga": lga_obj,
                    "employer": emp,
                    "business_branch": branch,
                    "work_location": work_loc,
                    "food_handler_category": category,
                    "system_identifier": sid,
                    "current_status": status,
                },
            )
            return obj

        ada_fh = _fh(ada_user, "Ada Okafor", date(1990, 3, 15), Gender.FEMALE, "12345678901", "08010000001", "ada.okafor@example.com", "15 Alade Street, Ikeja", ikeja, "MegaChow — Ikeja Kitchen", FoodHandlerCategory.KITCHEN_STAFF, mega_emp, mega_ikeja)
        bola_fh = _fh(bola_user, "Bola Surulere", date(1992, 6, 22), Gender.FEMALE, "98765432109", "08010000002", "bola.surulere@example.com", "8 Bode Thomas, Surulere", surulere, "MegaChow — Surulere Dining", FoodHandlerCategory.FOOD_PREPARER, mega_emp, mega_surulere)
        emeka_fh = _fh(emeka_user, "Emeka Nnamdi", date(1988, 11, 5), Gender.MALE, "55566677788", "08010000003", "emeka.nnamdi@example.com", "22 Awolowo Way, Ikeja", ikeja, "MegaChow — Ikeja Bar", FoodHandlerCategory.BARTENDER, mega_emp, mega_ikeja, status=FoodHandlerStatus.NIN_PENDING)
        chioma_fh = _fh(chioma_user, "Chioma Eze", date(1994, 1, 30), Gender.FEMALE, "11122233344", "08010000004", "chioma.eze@example.com", "7 Opebi Road, Ikeja", ikeja, "MegaChow — Ikeja Service", FoodHandlerCategory.SERVING_CATERING, mega_emp, mega_ikeja, status=FoodHandlerStatus.TEMPORARILY_EXCLUDED)

        # ── NIN verifications ──
        from apps.nin_verification.models import NINVerification, NINVerificationStatus

        def _nin(fh, nin_val, status, full_name=None, dob_val=None, gen=None, score=0.95, mismatches=None):
            from apps.nin_verification.models import NINVerification, NINVerificationStatus
            NINVerification.objects.get_or_create(
                food_handler=fh, nin=nin_val,
                defaults={
                    "provider": "mock",
                    "status": status,
                    "verified_full_name": full_name or "",
                    "verified_date_of_birth": dob_val,
                    "verified_gender": gen or "",
                    "match_score": score,
                    "mismatch_fields": mismatches or {},
                    "verified_at": timezone.now() if status == NINVerificationStatus.VERIFIED else None,
                },
            )

        _nin(ada_fh, "12345678901", NINVerificationStatus.VERIFIED, "Ada Okafor", date(1990, 3, 15), "female", 0.95)
        _nin(bola_fh, "98765432109", NINVerificationStatus.VERIFIED, "Bola Surulere", date(1992, 6, 22), "female", 0.97)
        _nin(emeka_fh, "55566677788", NINVerificationStatus.PENDING_VERIFICATION, "", None, "", 0.0)
        _nin(chioma_fh, "11122233344", NINVerificationStatus.VERIFIED, "Chioma Eze", date(1994, 1, 30), "female", 0.93)

        # ── assessment fee ──
        from apps.payments.models import AssessmentFee

        AssessmentFee.objects.get_or_create(
            state=lagos, facility_type=excel_fac.facility_type,
            defaults={
                "amount": "5000.00",
                "state_fee": "800.00",
                "facility_fee": "3500.00",
                "platform_fee": "700.00",
                "effective_from": date.today() - timedelta(days=365),
                "status": "active",
                "created_by": la_state,
            },
        )

        # ── payment transactions ──
        from apps.payments.models import PaymentTransaction, PaymentStatus

        def _pay(user, amount, ref, entity_type="food_handler", entity_id=None, paid=True):
            return PaymentTransaction.objects.get_or_create(
                internal_reference=ref,
                defaults={
                    "payer_user": user,
                    "payer_type": "food_handler",
                    "related_entity_type": entity_type,
                    "related_entity_id": entity_id or uuid4(),
                    "amount": amount,
                    "currency": "NGN",
                    "payment_provider": "mock",
                    "provider_reference": f"mock-{ref}",
                    "status": PaymentStatus.SUCCESS if paid else PaymentStatus.PENDING,
                    "paid_at": timezone.now() if paid else None,
                },
            )[0]

        ada_pay = _pay(ada_user, "5000.00", "REF-ADA-001", entity_id=uuid4())
        bola_pay = _pay(bola_user, "5000.00", "REF-BOLA-001", entity_id=uuid4())
        chioma_pay = _pay(chioma_user, "5000.00", "REF-CHIOMA-001", entity_id=uuid4())

        # ── appointments ──
        from apps.assessments.models import Appointment, AppointmentStatus

        def _appt(fh, fac, dt, status=AppointmentStatus.COMPLETED):
            return Appointment.objects.get_or_create(
                food_handler=fh, facility=fac, appointment_date=dt,
                defaults={"status": status},
            )[0]

        appt_dt = timezone.now() - timedelta(days=12)
        ada_appt = _appt(ada_fh, excel_fac, appt_dt)
        bola_appt = _appt(bola_fh, excel_fac, appt_dt)
        chioma_appt = _appt(chioma_fh, excel_fac, appt_dt)

        # ── medical assessments ──
        from apps.assessments.models import MedicalAssessment, AssessmentStatus, FitnessDecision, StepStatus
        from apps.assessments.models import HealthDeclaration, PhysicalExamination

        def _assessment(fh, emp, fac, doc, appt, payment, fit=True):
            return MedicalAssessment.objects.get_or_create(
                food_handler=fh,
                defaults={
                    "employer": emp,
                    "facility": fac,
                    "doctor": doc,
                    "appointment": appt,
                    "assessment_date": appt.appointment_date,
                    "payment_transaction": payment,
                    "status": AssessmentStatus.CERTIFICATE_ISSUED if fit else AssessmentStatus.CLOSED,
                    "declaration_status": StepStatus.VALIDATED,
                    "physical_exam_status": StepStatus.COMPLETED,
                    "lab_status": StepStatus.REVIEWED,
                    "vaccination_status": StepStatus.REVIEWED,
                    "final_decision": FitnessDecision.FIT if fit else FitnessDecision.NOT_FIT,
                    "doctor_notes": "All clear. Food handler is fit to handle food." if fit else "Requires treatment before clearance.",
                    "signed_at": timezone.now(),
                },
            )[0]

        ada_assmt = _assessment(ada_fh, mega_emp, excel_fac, excel_doc, ada_appt, ada_pay)
        bola_assmt = _assessment(bola_fh, mega_emp, excel_fac, excel_doc, bola_appt, bola_pay)
        chioma_assmt = _assessment(chioma_fh, mega_emp, excel_fac, excel_doc, chioma_appt, chioma_pay)

        # ── health declarations ──
        for assmt in [ada_assmt, bola_assmt, chioma_assmt]:
            HealthDeclaration.objects.get_or_create(
                assessment=assmt,
                defaults={
                    "diarrhoea_vomiting_last_7_days": False,
                    "fever_more_than_one_week": False,
                    "skin_trouble": False,
                    "boils_styes_sepsis": False,
                    "discharge_eye_ear_nose_mouth": False,
                    "recurring_skin_or_ear_infection": False,
                    "recurring_bowel_disorder": False,
                    "cholera_contact_last_5_days": False,
                    "diarrhoea_vomiting_contact_last_7_days": False,
                    "typhoid_paratyphoid_jaundice_contact_last_21_days": False,
                    "typhoid_or_paratyphoid_carrier": False,
                    "previous_or_current_typhoid": False,
                    "certified_true": True,
                    "risk_flag": False,
                    "submitted_at": timezone.now(),
                    "validated_by_doctor": excel_doc,
                    "validated_at": timezone.now(),
                },
            )

        # ── physical examinations ──
        for assmt in [ada_assmt, bola_assmt, chioma_assmt]:
            PhysicalExamination.objects.get_or_create(
                assessment=assmt,
                defaults={
                    "fever": False,
                    "jaundice": False,
                    "skin_infection": False,
                    "boils_styes_sepsis": False,
                    "discharge": False,
                    "diarrhoea": False,
                    "vomiting": False,
                    "sore_throat_with_fever": False,
                    "cough_or_flu": False,
                    "known_typhoid_carrier_history": False,
                    "other_notes": "No significant findings.",
                    "examined_by": excel_doc,
                    "examined_at": timezone.now(),
                },
            )

        # ── lab tests ──
        from apps.lab_tests.models import LabTest, LabTestType, LabTestStatus

        for assmt in [ada_assmt, bola_assmt, chioma_assmt]:
            for ttype, name in [(LabTestType.STOOL_MICROSCOPY, "Stool Microscopy"), (LabTestType.STOOL_CULTURE_SENSITIVITY, "Stool Culture & Sensitivity"), (LabTestType.HEPATITIS_A_ANTIGEN, "Hepatitis A Antigen")]:
                LabTest.objects.get_or_create(
                    assessment=assmt, test_type=ttype,
                    defaults={
                        "test_name": name,
                        "status": LabTestStatus.REVIEWED,
                        "result_value": "Negative",
                        "result_notes": "No pathogens detected.",
                        "requested_by": excel_doc,
                        "resulted_by": users["excel.lab"],
                        "reviewed_by": excel_doc,
                        "requested_at": timezone.now(),
                        "resulted_at": timezone.now(),
                        "reviewed_at": timezone.now(),
                    },
                )

        # ── vaccinations ──
        from apps.vaccinations.models import VaccinationRecord, VaccineType, VaccinationStatus

        for fh in [ada_fh, bola_fh, chioma_fh]:
            VaccinationRecord.objects.get_or_create(
                food_handler=fh, vaccine_type=VaccineType.TYPHOID, dose_number=1,
                defaults={
                    "vaccine_name": "Typhoid Vi Polysaccharide",
                    "date_administered": date.today() - timedelta(days=60),
                    "expiry_date": date.today() + timedelta(days=365 * 3 - 60),
                    "status": VaccinationStatus.VALID,
                    "doctor_clearance": True,
                    "notes": "Valid until 3 years from administration",
                    "recorded_by": excel_doc,
                    "reviewed_at": timezone.now(),
                },
            )
            VaccinationRecord.objects.get_or_create(
                food_handler=fh, vaccine_type=VaccineType.HEPATITIS_A, dose_number=1,
                defaults={
                    "vaccine_name": "Hepatitis A Vaccine",
                    "date_administered": date.today() - timedelta(days=90),
                    "expiry_date": date.today() + timedelta(days=365 * 3 - 90),
                    "status": VaccinationStatus.SECOND_DOSE_DUE,
                    "doctor_clearance": True,
                    "notes": "Second dose due at 6 months",
                    "recorded_by": excel_doc,
                    "reviewed_at": timezone.now(),
                },
            )

        # ── certificates ──
        from apps.certificates.models import Certificate, CertificateStatus, CertificateRequestStatus, CertificateRequest
        from apps.certificates.services import CertificateService

        def _issue_cert(assmt, fh, fac, doc, state_):
            existing = Certificate.objects.filter(assessment=assmt).first()
            if existing:
                return existing
            cert_request = CertificateRequest.objects.create(
                assessment=assmt,
                requested_by=doc,
                status=CertificateRequestStatus.APPROVED,
                reviewed_by=la_state,
            )
            return CertificateService.issue_certificate(assessment=assmt, actor=la_state)

        ada_cert = _issue_cert(ada_assmt, ada_fh, excel_fac, excel_doc, lagos)
        bola_cert = _issue_cert(bola_assmt, bola_fh, excel_fac, excel_doc, lagos)
        chioma_cert = _issue_cert(chioma_assmt, chioma_fh, excel_fac, excel_doc, lagos)

        # ── illness report (Chioma only) ──
        from apps.illness.models import IllnessReport, SuspectedCondition, ClearanceStatus

        IllnessReport.objects.get_or_create(
            food_handler=chioma_fh, employer=mega_emp,
            defaults={
                "reported_by": mega_hq_u,
                "symptoms": {"diarrhoea": True, "vomiting": True},
                "suspected_condition": "general_diarrhoea_vomiting",
                "symptom_start_date": date.today() - timedelta(days=5),
                "symptom_end_date": date.today() - timedelta(days=3),
                "exclusion_start_date": date.today() - timedelta(days=5),
                "earliest_return_date": date.today() + timedelta(days=1),
                "clearance_required": True,
                "clearance_status": ClearanceStatus.PENDING,
                "reviewed_by_doctor": excel_doc,
            },
        )

        # ── summary ──
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Seed complete. {created_count} users created."))
        self.stdout.write("")
        self.stdout.write("─" * 80)
        self.stdout.write(f"{'Username':<22} {'Password':<14} {'Role':<24} {'Portal'}")
        self.stdout.write("─" * 80)

        rows = [
            ("super.admin", "super_admin", "/federal/dashboard"),
            ("federal.admin", "federal_admin", "/federal/dashboard"),
            ("lagos.admin", "state_admin", "/state/dashboard"),
            ("lagos.verifier", "state_admin", "/state/dashboard"),
            ("lagos.accreditor", "state_admin", "/state/dashboard"),
            ("lagos.inspector", "inspector", "/inspector/dashboard"),
            ("excel.admin", "facility_admin", "/facility/dashboard"),
            ("excel.doctor", "doctor", "/doctor/dashboard"),
            ("excel.lab", "lab_staff", "/lab/dashboard"),
            ("prime.admin", "facility_admin", "/facility/dashboard"),
            ("megachow.hq", "employer", "/employer/dashboard"),
            ("megachow.ikeja", "employer", "/employer/dashboard"),
            ("megachow.surulere", "employer", "/employer/dashboard"),
            ("ada.okafor", "food_handler", "/food-handler/dashboard"),
            ("bola.surulere", "food_handler", "/food-handler/dashboard"),
            ("emeka.nnamdi", "food_handler", "/food-handler/dashboard"),
            ("chioma.eze", "food_handler", "/food-handler/dashboard"),
        ]

        from apps.accounts.models import UserRole

        ROLE_LABELS_L = dict(UserRole.choices)

        for username, role, portal in rows:
            self.stdout.write(f"{username:<22} {DEMO_PASSWORD:<14} {ROLE_LABELS_L.get(role, role):<24} {portal}")

        self.stdout.write("─" * 80)
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("Demo scenarios:"))
        self.stdout.write("  ada.okafor     — Fit to Handle Food (full journey, certificate ready)")
        self.stdout.write("  bola.surulere  — Fit to Handle Food (Surulere branch, demonstrates branch isolation)")
        self.stdout.write("  emeka.nnamdi   — NIN Pending (certificate blocked)")
        self.stdout.write("  chioma.eze     — Temporarily Excluded (diarrhoea, return-to-work pending)")
        self.stdout.write("")
        self.stdout.write("  megachow.hq    — Head office (sees all 4 handlers)")
        self.stdout.write("  megachow.ikeja — Branch manager Ikeja (sees Ada + Chioma only)")
        self.stdout.write("  megachow.surulere — Branch manager Surulere (sees Bola only)")
        self.stdout.write("")

    def _clear_demo_data(self):
        from apps.accounts.models import UserInvite
        from apps.certificates.models import Certificate, CertificateRequest, CertificateVerificationLog
        from apps.assessments.models import MedicalAssessment, HealthDeclaration, PhysicalExamination, Appointment
        from apps.lab_tests.models import LabTest
        from apps.vaccinations.models import VaccinationRecord
        from apps.illness.models import IllnessReport
        from apps.nin_verification.models import NINVerification
        from apps.payments.models import PaymentTransaction, AssessmentFee
        from apps.settlements.models import Settlement
        from apps.food_handlers.models import FoodHandlerProfile
        from apps.employers.models import Employer
        from apps.facilities.models import MedicalFacility, FacilityAccreditationApplication
        from apps.organizations.models import OrganizationUnit, Organization
        from apps.policy.models import StatePolicyConfig

        models = [
            CertificateVerificationLog, Settlement, IllnessReport, LabTest,
            VaccinationRecord, PhysicalExamination, HealthDeclaration,
            Certificate, CertificateRequest, MedicalAssessment, Appointment,
            PaymentTransaction, AssessmentFee, NINVerification,
            FoodHandlerProfile, Employer, FacilityAccreditationApplication,
            MedicalFacility, UserInvite, OrganizationUnit, Organization,
            StatePolicyConfig,
        ]
        for m in models:
            m.objects.all().delete()

        User.objects.exclude(is_superuser=True).delete()
        self.stdout.write(self.style.WARNING("All demo data cleared."))
