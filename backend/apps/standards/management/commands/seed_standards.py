from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.standards.models import (
    CertificateTemplate,
    CertificateValidityRule,
    EstablishmentCategory,
    FacilityRequirementRule,
    FoodHandlerCategory,
    MEIndicator,
    MedicalTestRule,
    PhysicalExaminationRule,
    PolicyVersion,
    ReportingTemplate,
    ReturnToWorkRule,
    StateConfigurationControl,
    VaccinationRule,
)


class Command(BaseCommand):
    help = "Seed baseline 2024 National Guideline standards"

    def handle(self, *args, **options):
        if PolicyVersion.objects.filter(version_code="NG-FHMT-2024-v1.0").exists():
            self.stdout.write(self.style.WARNING("Baseline policy version already exists. Skipping."))
            return

        pv = PolicyVersion.objects.create(
            version_code="NG-FHMT-2024-v1.0",
            title="National Guidelines for Food Handlers' Medical Test — Baseline",
            description="Baseline configuration derived from the National Guidelines for Food Handlers' Medical Test.",
            version_type="major",
            status="active",
            effective_start_date=timezone.now(),
            requires_state_acknowledgement=True,
            change_summary="Initial baseline policy seeded from the national guideline.",
            published_at=timezone.now(),
        )
        self.stdout.write(f"Created policy version: {pv.version_code}")

        handler_categories = [
            ("Kitchen Staff", "FH-KITCHEN", "high"),
            ("Food Preparers", "FH-PREPARER", "high"),
            ("Serving and Catering Staff", "FH-SERVICE-CATERING", "medium"),
            ("Food Packers", "FH-PACKER", "medium"),
            ("Bakery Workers", "FH-BAKERY", "high"),
            ("Food Processing Operators", "FH-PROCESSING", "high"),
            ("Bartenders", "FH-BARTENDER", "medium"),
            ("Dishwashers", "FH-DISHWASHER", "medium"),
            ("Food Delivery Personnel", "FH-DELIVERY", "low"),
            ("Food Stall and Street Food Vendors", "FH-STREET-VENDOR", "high"),
            ("Food Storage Handlers", "FH-STORAGE", "medium"),
            ("Concession Stand Workers", "FH-CONCESSION", "medium"),
            ("Airline Catering Vendors", "FH-AIRLINE-CATERING", "high"),
            ("Train Catering Vendors", "FH-TRAIN-CATERING", "high"),
            ("Cruise Ship / Sea Vessel Catering Vendors", "FH-SEA-CATERING", "high"),
            ("Livestock Farmers", "FH-LIVESTOCK", "medium"),
            ("Emergency Situation Workers", "FH-EMERGENCY", "high"),
        ]
        for name, code, risk in handler_categories:
            FoodHandlerCategory.objects.create(
                policy_version=pv, name=name, code=code,
                risk_level=risk, certificate_required=True,
                nationally_locked=True, status="active",
            )
        self.stdout.write(f"  Seeded {len(handler_categories)} food handler categories")

        establishment_categories = [
            ("Restaurants and Cafes", "EST-RESTAURANT", "high"),
            ("Bakeries and Pastry Shops", "EST-BAKERY", "high"),
            ("Abattoirs, Slaughter Slabs, and Butcher Shops", "EST-ABATTOIR", "high"),
            ("Grocery Stores and Supermarkets", "EST-GROCERY", "medium"),
            ("Food Trucks and Street Vendors", "EST-STREET", "high"),
            ("Catering Services", "EST-CATERING", "high"),
            ("School Cafeterias", "EST-SCHOOL", "high"),
            ("Hospital Kitchens", "EST-HOSPITAL", "high"),
            ("Bars and Pubs", "EST-BAR", "medium"),
            ("Food Processing Plants", "EST-PROCESSING", "high"),
            ("Hotels and Resorts", "EST-HOTEL", "high"),
            ("Corporate Dining Facilities", "EST-CORPORATE", "medium"),
            ("Food Markets and Stalls", "EST-MARKET", "medium"),
            ("Airports and Train Stations", "EST-TRANSPORT", "high"),
            ("Farms and Livestock Feed Processing Plants", "EST-FARM", "medium"),
            ("Daycare Centres", "EST-DAYCARE", "high"),
        ]
        for name, code, risk in establishment_categories:
            EstablishmentCategory.objects.create(
                policy_version=pv, name=name, code=code,
                risk_level=risk, status="active",
            )
        self.stdout.write(f"  Seeded {len(establishment_categories)} establishment categories")

        MedicalTestRule.objects.create(
            policy_version=pv,
            name="Stool Microscopy, Culture and Sensitivity",
            code="LAB-STOOL-MCS",
            test_type="laboratory",
            rule_type="mandatory",
            result_type="positive_negative",
            accepted_values=["negative"],
            blocking_values=["positive"],
            blocks_certification=True,
            requires_attachment=False,
            requires_doctor_validation=True,
            requires_lab_validation=True,
            validity_days=180,
            status="active",
        )
        MedicalTestRule.objects.create(
            policy_version=pv,
            name="Hepatitis A Antigen",
            code="LAB-HEPA-AG",
            test_type="laboratory",
            rule_type="mandatory",
            result_type="positive_negative",
            accepted_values=["negative"],
            blocking_values=["positive"],
            blocks_certification=True,
            requires_attachment=False,
            requires_doctor_validation=True,
            requires_lab_validation=True,
            validity_days=180,
            status="active",
        )
        MedicalTestRule.objects.create(
            policy_version=pv,
            name="Additional Clinically Indicated Test",
            code="LAB-CLINICAL-ADDITIONAL",
            test_type="clinical",
            rule_type="conditional",
            result_type="text",
            blocks_certification=False,
            requires_doctor_validation=True,
            status="active",
        )
        self.stdout.write("  Seeded 3 medical test rules")

        physical_indicators = [
            ("Fever", "PE-FEVER", "high", True, True),
            ("Jaundice", "PE-JAUNDICE", "critical", True, True),
            ("Skin infections on hands, arms, or face", "PE-SKIN-INFECTION", "high", True, True),
            ("Boils, styes, or sepsis on fingers", "PE-BOILS", "high", True, True),
            ("Discharge from eyes, nose, ears, or mouth", "PE-DISCHARGE", "medium", True, False),
            ("Diarrhoea and/or vomiting", "PE-DIARRHOEA", "critical", True, True),
            ("Known history of being a typhoid carrier", "PE-TYPHOID-CARRIER", "critical", True, True),
            ("Sore throat", "PE-SORE-THROAT", "medium", False, False),
            ("Cough or flu", "PE-COUGH-FLU", "low", False, False),
        ]
        for name, code, severity, blocks, excludes in physical_indicators:
            PhysicalExaminationRule.objects.create(
                policy_version=pv,
                indicator_name=name, code=code,
                severity=severity,
                blocks_certification=blocks,
                requires_exclusion=excludes,
                requires_doctor_notes=True,
                requires_reexamination=blocks,
                public_health_escalation=severity in ("critical",),
                status="active",
            )
        self.stdout.write(f"  Seeded {len(physical_indicators)} physical examination indicators")

        VaccinationRule.objects.create(
            policy_version=pv,
            vaccine_name="Typhoid Fever Vaccine",
            vaccine_code="VAC-TYPHOID",
            required=True,
            dose_schedule=[{"dose": 1, "interval_months": 0}],
            validity_months=36,
            grace_period_days=30,
            evidence_required=True,
            evidence_fields=["vaccination_date", "brand", "batch_number", "vaccinator", "facility", "next_visit"],
            blocks_certification_if_missing=True,
            blocks_certification_if_expired=True,
            requires_doctor_prescription_if_missing=True,
            status="active",
        )
        VaccinationRule.objects.create(
            policy_version=pv,
            vaccine_name="Hepatitis A Vaccine",
            vaccine_code="VAC-HEPA",
            required=True,
            dose_schedule=[
                {"dose": 1, "interval_months": 0},
                {"dose": 2, "interval_months": 6},
            ],
            validity_months=None,
            grace_period_days=30,
            evidence_required=True,
            evidence_fields=["vaccination_date", "brand", "batch_number", "vaccinator", "facility", "next_visit"],
            blocks_certification_if_missing=True,
            blocks_certification_if_expired=False,
            requires_doctor_prescription_if_missing=True,
            status="active",
        )
        VaccinationRule.objects.create(
            policy_version=pv,
            vaccine_name="Other Required Vaccine",
            vaccine_code="VAC-OTHER",
            required=False,
            dose_schedule=[],
            evidence_required=True,
            blocks_certification_if_missing=False,
            blocks_certification_if_expired=False,
            status="active",
        )
        self.stdout.write("  Seeded 3 vaccination rules")

        CertificateTemplate.objects.create(
            policy_version=pv,
            template_name="National Food Handler Certificate",
            template_version="1.0",
            layout_config={
                "sections": ["header", "identity", "assessment_summary", "vaccination_summary", "issuing_authority", "qr_code", "footer"],
            },
            required_fields=[
                "certificate_id", "qr_code", "full_name", "date_of_birth", "gender",
                "passport_photograph", "nin", "state_of_domicile", "employer_name",
                "medical_facility_name", "doctor_name", "assessment_date",
                "issue_date", "expiry_date", "fitness_status", "vaccination_summary",
                "policy_version", "issuing_authority", "digital_signature",
            ],
            certificate_number_format="FHMT-{STATE}-{YYYY}-{SEQ}",
            qr_payload_config={
                "fields": ["certificate_id", "verification_token", "issuing_authority", "policy_version", "verification_url", "checksum"],
            },
            public_verification_fields=[
                "certificate_status", "handler_name", "passport_photograph",
                "certificate_id", "issue_date", "expiry_date", "state",
                "medical_facility", "fitness_status", "verification_timestamp",
            ],
            status_rules={
                "statuses": ["draft", "valid", "expired", "revoked", "suspended", "not_fit", "cleared_to_return", "under_review"],
            },
            revocation_reasons=[
                "fraudulent_documentation", "failed_re_examination",
                "facility_accreditation_revoked", "public_health_order",
                "handler_request", "employer_request", "administrative_error",
            ],
            status="active",
        )
        self.stdout.write("  Seeded certificate template")

        CertificateValidityRule.objects.create(
            policy_version=pv,
            routine_assessment_interval_days=180,
            certificate_validity_days=365,
            renewal_window_days=30,
            grace_period_days=0,
            expiry_reminder_days=[30, 14, 7],
            illness_suspension_enabled=True,
            emergency_revalidation_enabled=False,
            status="active",
        )
        self.stdout.write("  Seeded certificate validity rule")

        rtw_conditions = [
            ("Diarrhoea / Vomiting", "RTW-DIARRHOEA", 48, True, False, 0, False),
            ("Cholera", "RTW-CHOLERA", 168, True, True, 2, True),
            ("Hepatitis A", "RTW-HEPA", 336, True, True, 1, True),
            ("Infected Skin Lesion", "RTW-SKIN", 0, True, False, 0, False),
            ("Lassa Fever", "RTW-LASSA", 504, True, True, 2, True),
        ]
        for name, code, hours, med, lab, samples, authority in rtw_conditions:
            ReturnToWorkRule.objects.create(
                policy_version=pv,
                condition_name=name, condition_code=code,
                default_exclusion_hours=hours,
                requires_medical_clearance=med,
                requires_lab_clearance=lab,
                negative_samples_required=samples if samples else None,
                requires_health_authority_approval=authority,
                employer_acknowledgement_required=True,
                clearance_document_required=True,
                status="active",
            )
        self.stdout.write(f"  Seeded {len(rtw_conditions)} return-to-work rules")

        facility_requirements = [
            ("Written reporting and documentation policy", "FREQ-DOC-POLICY", "documentation", True, "file"),
            ("Computers and operators in medical records unit", "FREQ-COMPUTERS", "digital_infrastructure", True, "inspection"),
            ("Pre-defined health declaration forms", "FREQ-DECLARATION-FORMS", "documentation", True, "checklist"),
            ("Patient files for doctor notes", "FREQ-PATIENT-FILES", "records", True, "inspection"),
            ("Certificate formats containing QR codes", "FREQ-QR-CERT", "certification", True, "inspection"),
            ("Internet access", "FREQ-INTERNET", "digital_infrastructure", True, "inspection"),
            ("Trained clinical and non-clinical staff", "FREQ-TRAINED-STAFF", "staffing", True, "file"),
            ("Standard medical record management process", "FREQ-RECORD-MGMT", "records", True, "checklist"),
            ("Confidentiality and safe storage policy", "FREQ-CONFIDENTIALITY", "records", True, "file"),
            ("Annual re-accreditation", "FREQ-REACCREDITATION", "reaccreditation", True, "file"),
        ]
        for name, code, cat, mandatory, evidence in facility_requirements:
            FacilityRequirementRule.objects.create(
                policy_version=pv,
                requirement_name=name, requirement_code=code,
                category=cat, mandatory=mandatory,
                evidence_type=evidence,
                renewal_required=(cat == "reaccreditation"),
                renewal_interval_days=365 if cat == "reaccreditation" else None,
                status="active",
            )
        self.stdout.write(f"  Seeded {len(facility_requirements)} facility requirement rules")

        ReportingTemplate.objects.create(
            policy_version=pv,
            template_name="Quarterly State Performance Report",
            template_code="RPT-STATE-QUARTERLY",
            reporting_frequency="quarterly",
            deadline_rule={"days_after_period_end": 15},
            required_sections=[
                "state_summary", "total_food_handlers_registered",
                "total_certified_food_handlers", "total_expired_certificates",
                "total_unfit_handlers", "total_approved_medical_facilities",
                "facility_reaccreditation_status", "vaccination_coverage",
                "illness_and_exclusion_reports", "enforcement_actions",
                "public_awareness_activities", "challenges",
                "recommendations", "data_quality_issues",
            ],
            required_indicators=[],
            required_uploads=["signed_summary_letter"],
            scoring_config={
                "total_weight": 100,
                "section_weights": {"state_summary": 10, "data_quality_issues": 5},
            },
            approval_required=True,
            status="active",
        )
        self.stdout.write("  Seeded reporting template")

        me_indicators = [
            ("Food Handler Certification Rate", "ME-CERT-RATE", "certificate_records", "quarterly", "card", True, "automatic", "percentage", "certificates", "FH-VALIDITY-2024-001", ""),
            ("Vaccination Compliance Rate", "ME-VAX-RATE", "medical_test_records", "quarterly", "bar", True, "manual", "", "", "", ""),
            ("Expired Certificate Rate", "ME-EXPIRED-RATE", "certificate_records", "monthly", "line", True, "automatic", "percentage", "certificates", "FH-VALIDITY-2024-001", "certificate_validity_months"),
            ("Facility Accreditation Compliance", "ME-FACILITY-ACCRED", "facility_records", "quarterly", "bar", True, "automatic", "percentage", "medical_facilities", "FH-FAC-2024-001", "reaccreditation_interval_months"),
            ("State Reporting Compliance", "ME-STATE-REPORT", "manual", "quarterly", "table", True, "manual", "", "", "", ""),
            ("QR Verification Failure Rate", "ME-QR-FAIL", "inspections", "monthly", "line", False, "automatic", "percentage", "qr_verification_logs", "FH-CERT-2024-001", "requires_qr_code"),
            ("Unfit Detection Rate", "ME-UNFIT-RATE", "test_results", "quarterly", "card", True, "manual", "", "", "", ""),
            ("Return-to-Work Clearance Rate", "ME-RTW-RATE", "medical_test_records", "quarterly", "card", False, "hybrid", "percentage", "return_to_work_clearances", "FH-RTW-2024-001", "standard_exclusion_period_hours_after_symptoms_stop"),
            ("Data Completeness Score", "ME-DATA-COMPLETE", "food_handler_registry", "quarterly", "card", True, "automatic", "percentage", "system_required_fields", "", ""),
        ]
        for name, code, source, freq, viz, mandatory, input_mode, calculation_type, calculation_source, policy_standard_code, rule_parameter_key in me_indicators:
            MEIndicator.objects.create(
                policy_version=pv,
                indicator_name=name, indicator_code=code,
                data_source=source, reporting_frequency=freq,
                visualization_type=viz, mandatory=mandatory,
                input_mode=input_mode,
                calculation_type=calculation_type,
                calculation_source=calculation_source,
                policy_standard_code=policy_standard_code,
                rule_parameter_key=rule_parameter_key,
                allow_manual_override=input_mode == "hybrid",
                override_requires_reason=input_mode == "hybrid",
                federal_dashboard_visible=True,
                state_dashboard_visible=True,
                status="active",
            )
        self.stdout.write(f"  Seeded {len(me_indicators)} M&E indicators")

        state_controls = [
            ("medical_test_minimums", "Medical Test Minimums", True, False, False),
            ("vaccination_minimums", "Vaccination Minimums", True, False, False),
            ("handler_categories", "Handler Categories", True, True, False),
            ("establishment_categories", "Establishment Categories", True, True, False),
            ("facility_approval", "Facility Approval", False, True, True),
            ("assessment_prices", "Assessment Prices", False, True, False),
            ("reporting_templates", "Reporting Templates", True, False, False),
            ("enforcement_actions", "Enforcement Actions", False, True, False),
        ]
        for domain, label, locked, editable, approval in state_controls:
            StateConfigurationControl.objects.create(
                policy_version=pv,
                config_domain=domain, label=label,
                federal_locked=locked,
                state_editable=editable,
                requires_federal_approval=approval,
            )
        self.stdout.write(f"  Seeded {len(state_controls)} state configuration controls")

        self.stdout.write(self.style.SUCCESS("Baseline 2024 standards seeded successfully."))
