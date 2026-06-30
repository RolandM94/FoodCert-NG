from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.standards.models import (
    CertificateTemplate,
    CertificateValidityRule,
    EstablishmentCategory,
    FacilityRequirementRule,
    FoodHandlerCategory,
    MEIndicator,
    MedicalTestPackage,
    MedicalTestPackageComponent,
    MedicalTestPackageComponentType,
    MedicalTestRule,
    PhysicalExaminationRule,
    PolicyVersion,
    ReportingTemplate,
    ReturnToWorkRule,
    StateConfigurationControl,
    VaccinationRule,
)


class Command(BaseCommand):
    help = (
        "Seed the Food Handlers 2024 Policy Version (FH-POL-2024-001) "
        "with 16 attached standards derived from the National Guidelines "
        "for Food Handlers' Medical Test 2024."
    )

    def handle(self, *args, **options):
        if PolicyVersion.objects.filter(version_code="FH-POL-2024-001").exists():
            self.stdout.write(self.style.WARNING(
                "FH-POL-2024-001 already exists. Skipping seed."
            ))
            return

        pv = PolicyVersion.objects.create(
            version_code="FH-POL-2024-001",
            title="National Guidelines for Food Handlers' Medical Test",
            description=(
                "The national guideline establishing medical assessment, "
                "certification, vaccination, documentation, monitoring, "
                "and regulatory standards for food handlers in Nigeria. "
                "This policy version is extracted from the 2024 National "
                "Guidelines for Food Handlers' Medical Test."
            ),
            version_type="major",
            status="active",
            effective_start_date=timezone.make_aware(
                timezone.datetime(2024, 12, 1),
            ),
            requires_state_acknowledgement=True,
            change_summary=(
                "Initial seeding of FH-POL-2024-001 with 16 standards "
                "derived from the National Guidelines for Food Handlers' "
                "Medical Test 2024."
            ),
            published_at=timezone.now(),
        )
        self.stdout.write(f"Created policy version: {pv.version_code}")

        # ── 2.1  FH-SCOPE-2024-001 — Scope of Covered Food Handlers ──
        self._seed_handler_categories(pv)

        # ── 2.2  FH-EST-2024-001 — Covered Food Establishments ──
        self._seed_establishment_categories(pv)

        # ── 2.3  FH-FAC-2024-001 — Medical Facility Prequalification ──
        self._seed_facility_accreditation(pv)

        # ── 2.4  FH-ASSMT-2024-001 — Medical Assessment Workflow ──
        self._seed_assessment_workflow(pv)

        # ── 2.5  FH-TEST-2024-001 — Mandatory Laboratory Test Standard ──
        self._seed_lab_tests(pv)

        # ── 2.6  FH-VACC-2024-001 — Vaccination Requirement Standard ──
        self._seed_vaccination_rules(pv)

        # ── 2.7  FH-VALIDITY-2024-001 — Certificate & Assessment Validity ──
        self._seed_validity_rule(pv)

        # ── 2.8  FH-CERT-2024-001 — Certificate Issuance & QR Verification ──
        self._seed_certificate_template(pv)

        # ── 2.9  FH-ILL-2024-001 — Illness Reporting and Exclusion ──
        self._seed_illness_exclusion(pv)

        # ── 2.10 FH-RTW-2024-001 — Return-to-Work Clearance ──
        self._seed_return_to_work(pv)

        # ── 2.11 FH-DOC-2024-001 — Medical Records and Documentation ──
        self._seed_documentation_rules(pv)

        # ── 2.12 FH-ID-2024-001 — Food Handler Identity ──
        # (captured via certificate template identity fields above)

        # ── 2.13 FH-FBO-2024-001 — Food Business Owner Responsibility ──
        # ── 2.14 FH-HYGIENE-2024-001 — Food Handler Hygiene Practice ──
        # ── 2.15 FH-GOV-2024-001 — Government Oversight ──
        self._seed_state_config_controls(pv)

        # ── 2.16 FH-ME-2024-001 — Monitoring, Evaluation, Reporting ──
        self._seed_reporting(pv)

        self.stdout.write(self.style.SUCCESS(
            "FH-POL-2024-001 with 16 standards seeded successfully."
        ))

    # ───────────────────────── helpers ─────────────────────────

    def _seed_handler_categories(self, pv):
        categories = [
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
        for name, code, risk in categories:
            FoodHandlerCategory.objects.create(
                policy_version=pv,
                name=name,
                code=code,
                risk_level=risk,
                certificate_required=True,
                nationally_locked=True,
                status="active",
            )
        self.stdout.write(
            f"  FH-SCOPE-2024-001: {len(categories)} food handler categories"
        )

    def _seed_establishment_categories(self, pv):
        categories = [
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
        for name, code, risk in categories:
            EstablishmentCategory.objects.create(
                policy_version=pv,
                name=name,
                code=code,
                risk_level=risk,
                status="active",
            )
        self.stdout.write(
            f"  FH-EST-2024-001: {len(categories)} establishment categories"
        )

    def _seed_facility_accreditation(self, pv):
        FacilityRequirementRule.objects.create(
            policy_version=pv,
            requirement_name="State Mapping and Prequalification",
            requirement_code="FREQ-STATE-MAPPING",
            category="prequalification",
            mandatory=True,
            evidence_type="file",
            status="active",
        )
        FacilityRequirementRule.objects.create(
            policy_version=pv,
            requirement_name="Annual Re-Accreditation (12 months)",
            requirement_code="FREQ-REACCREDIT-12M",
            category="reaccreditation",
            mandatory=True,
            evidence_type="file",
            renewal_required=True,
            renewal_interval_days=365,
            status="active",
        )
        FacilityRequirementRule.objects.create(
            policy_version=pv,
            requirement_name="Assessment price standardization per state",
            requirement_code="FREQ-PRICE-STANDARD",
            category="pricing",
            mandatory=True,
            evidence_type="checklist",
            status="active",
        )
        FacilityRequirementRule.objects.create(
            policy_version=pv,
            requirement_name="Assessment reports valid only from prequalified facilities",
            requirement_code="FREQ-PREQUAL-VALIDATION",
            category="validation",
            mandatory=True,
            evidence_type="inspection",
            status="active",
        )
        FacilityRequirementRule.objects.create(
            policy_version=pv,
            requirement_name="Handlers must use approved facilities in respective state or FCT",
            requirement_code="FREQ-STATE-FACILITY",
            category="jurisdiction",
            mandatory=True,
            evidence_type="checklist",
            status="active",
        )
        self.stdout.write(
            "  FH-FAC-2024-001: 5 facility accreditation rules "
            "(12-month reaccreditation)"
        )

    def _seed_assessment_workflow(self, pv):
        indicators = [
            ("Fever", "PE-FEVER", "high", True, True, False),
            ("Jaundice", "PE-JAUNDICE", "critical", True, True, True),
            (
                "Skin infections on hands, arms, or face",
                "PE-SKIN-INFECTION", "high", True, True, False,
            ),
            (
                "Boils, styes, or sepsis on fingers",
                "PE-BOILS", "high", True, True, False,
            ),
            (
                "Discharge from eyes, nose, ears, or mouth",
                "PE-DISCHARGE", "medium", True, True, False,
            ),
            (
                "Diarrhea and/or vomiting",
                "PE-DIARRHOEA", "critical", True, True, True,
            ),
            (
                "Known history of being a typhoid carrier",
                "PE-TYPHOID-CARRIER", "critical", True, True, True,
            ),
            ("Sore throat", "PE-SORE-THROAT", "medium", True, True, False),
            ("Cough or flu", "PE-COUGH-FLU", "medium", True, False, False),
        ]
        for name, code, severity, doctor, excludes, escalation in indicators:
            PhysicalExaminationRule.objects.create(
                policy_version=pv,
                indicator_name=name,
                code=code,
                severity=severity,
                requires_doctor_notes=doctor,
                blocks_certification=True,
                requires_exclusion=excludes,
                requires_reexamination=excludes,
                public_health_escalation=escalation,
                status="active",
            )
        self.stdout.write(
            f"  FH-ASSMT-2024-001: {len(indicators)} physical examination "
            f"indicators (6-month assessment frequency enforced via validity rule)"
        )

    def _seed_lab_tests(self, pv):
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
        self.stdout.write("  FH-TEST-2024-001: 3 medical test rules")

    def _seed_vaccination_rules(self, pv):
        VaccinationRule.objects.create(
            policy_version=pv,
            vaccine_name="Typhoid Fever Vaccine",
            vaccine_code="VAC-TYPHOID",
            required=True,
            dose_schedule=[{"dose": 1, "interval_months": 0}],
            validity_months=36,
            grace_period_days=30,
            evidence_required=True,
            evidence_fields=[
                "vaccination_date", "brand", "batch_number",
                "vaccinator", "facility",
            ],
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
            evidence_fields=[
                "vaccination_date", "brand", "batch_number",
                "vaccinator", "facility",
            ],
            blocks_certification_if_missing=True,
            blocks_certification_if_expired=False,
            requires_doctor_prescription_if_missing=True,
            status="active",
        )
        self.stdout.write(
            "  FH-VACC-2024-001: 2 vaccination rules "
            "(Typhoid 36-month, Hepatitis A 2-dose at 0+6 months)"
        )

    def _seed_validity_rule(self, pv):
        CertificateValidityRule.objects.create(
            policy_version=pv,
            routine_assessment_interval_days=180,
            certificate_validity_days=180,
            renewal_window_days=30,
            grace_period_days=0,
            expiry_reminder_days=[30, 14, 7],
            illness_suspension_enabled=True,
            emergency_revalidation_enabled=False,
            status="active",
        )
        self.stdout.write(
            "  FH-VALIDITY-2024-001: assessment 180d, certificate 180d (6 months)"
        )

    def _seed_certificate_template(self, pv):
        CertificateTemplate.objects.create(
            policy_version=pv,
            template_name="National Food Handler Fitness Certificate",
            template_version="2024.1",
            layout_config={
                "sections": [
                    "header", "identity", "assessment_summary",
                    "vaccination_summary", "doctor_declaration",
                    "issuing_authority", "qr_code", "footer",
                ],
            },
            required_fields=[
                "certificate_id", "qr_code", "full_name", "date_of_birth",
                "gender", "passport_photograph", "nin", "state_of_domicile",
                "employer_name", "food_handler_category",
                "medical_facility_name", "doctor_name", "assessment_date",
                "laboratory_test_date", "vaccination_status",
                "issue_date", "expiry_date", "fitness_status",
                "policy_version", "issuing_authority", "digital_signature",
            ],
            certificate_number_format="FHMT-{STATE}-{YYYY}-{SEQ}",
            qr_payload_config={
                "fields": [
                    "certificate_id", "verification_token",
                    "policy_version", "verification_url", "checksum",
                ],
                "verification_enabled": True,
                "central_database_validation": True,
            },
            public_verification_fields=[
                "certificate_status", "handler_name", "passport_photograph",
                "certificate_id", "issue_date", "expiry_date", "state",
                "medical_facility", "fitness_status", "verification_timestamp",
            ],
            status_rules={
                "statuses": [
                    "draft", "valid", "expired", "revoked",
                    "suspended", "not_fit", "cleared_to_return", "under_review",
                ],
            },
            revocation_reasons=[
                "fraudulent_documentation", "failed_re_examination",
                "facility_accreditation_revoked", "public_health_order",
                "handler_request", "employer_request", "administrative_error",
            ],
            status="active",
        )
        self.stdout.write("  FH-CERT-2024-001: certificate template with QR and central DB verification")

    def _seed_illness_exclusion(self, pv):
        conditions = [
            (
                "Exclusion (Standard — 48 hours)",
                "RTW-EXCLUDE-48H", 48, True, False, 0, 0, False, True, True,
            ),
        ]
        for (
            name, code, hours, med, lab, samples, sample_int,
            authority, employer, clearance,
        ) in conditions:
            ReturnToWorkRule.objects.create(
                policy_version=pv,
                condition_name=name,
                condition_code=code,
                default_exclusion_hours=hours,
                requires_medical_clearance=med,
                requires_lab_clearance=lab,
                negative_samples_required=samples if samples else None,
                sample_interval_hours=sample_int if sample_int else None,
                requires_health_authority_approval=authority,
                employer_acknowledgement_required=employer,
                clearance_document_required=clearance,
                status="active",
            )
        self.stdout.write("  FH-ILL-2024-001: illness exclusion rules")

    def _seed_return_to_work(self, pv):
        pathogen_rules = [
            (
                "Vibrio cholerae",
                "RTW-CHOLERA",
                168, True, True, 2, 24, True, True, True,
            ),
            (
                "Shigella dysenteriae, flexneri, and boydii",
                "RTW-SHIGELLA",
                168, True, True, 2, 48, False, True, True,
            ),
            (
                "Hepatitis A",
                "RTW-HEPA",
                168, True, False, 0, 0, True, True, True,
            ),
            (
                "Infected or injured skin",
                "RTW-SKIN",
                0, True, False, 0, 0, False, True, True,
            ),
            (
                "Entamoeba histolytica",
                "RTW-AMOEBA",
                168, True, True, 1, 168, False, True, True,
            ),
            (
                "Taenia solium",
                "RTW-TAENIA",
                168, True, True, 2, 168, False, True, True,
            ),
            (
                "Lassa Fever",
                "RTW-LASSA",
                504, True, False, 0, 0, True, True, True,
            ),
        ]
        for (
            name, code, hours, med, lab, samples, sample_int,
            authority, employer, clearance,
        ) in pathogen_rules:
            ReturnToWorkRule.objects.create(
                policy_version=pv,
                condition_name=name,
                condition_code=code,
                default_exclusion_hours=hours,
                requires_medical_clearance=med,
                requires_lab_clearance=lab,
                negative_samples_required=samples if samples else None,
                sample_interval_hours=sample_int if sample_int else None,
                requires_health_authority_approval=authority,
                employer_acknowledgement_required=employer,
                clearance_document_required=clearance,
                status="active",
            )
        self.stdout.write(
            f"  FH-RTW-2024-001: {len(pathogen_rules)} return-to-work rules"
        )

    def _seed_documentation_rules(self, pv):
        requirements = [
            (
                "Written reporting and documentation policy",
                "FREQ-DOC-POLICY", "documentation", True, "file", False, None,
            ),
            (
                "Computers and operators in medical records unit",
                "FREQ-COMPUTERS", "digital_infrastructure", True, "inspection", False, None,
            ),
            (
                "Pre-defined health declaration forms",
                "FREQ-DECLARATION-FORMS", "documentation", True, "checklist", False, None,
            ),
            (
                "Laboratory investigation request forms",
                "FREQ-LAB-REQ-FORMS", "documentation", True, "checklist", False, None,
            ),
            (
                "Radiology investigation request forms",
                "FREQ-RAD-REQ-FORMS", "documentation", True, "checklist", False, None,
            ),
            (
                "Patient files for doctor notes",
                "FREQ-PATIENT-FILES", "records", True, "inspection", False, None,
            ),
            (
                "Certificate formats containing QR codes",
                "FREQ-QR-CERT", "certification", True, "inspection", False, None,
            ),
            (
                "Internet access for central database",
                "FREQ-INTERNET", "digital_infrastructure", True, "inspection", False, None,
            ),
            (
                "Trained medical records staff",
                "FREQ-RECORDS-STAFF", "staffing", True, "file", False, None,
            ),
            (
                "Trained clinical team",
                "FREQ-CLINICAL-STAFF", "staffing", True, "file", False, None,
            ),
            (
                "Trained non-clinical team",
                "FREQ-NONCLINICAL-STAFF", "staffing", True, "file", False, None,
            ),
            (
                "Confidentiality and safe storage policy",
                "FREQ-CONFIDENTIALITY", "records", True, "file", False, None,
            ),
            (
                "Record retention policy",
                "FREQ-RETENTION", "records", True, "file", False, None,
            ),
            (
                "Support for hard-copy and electronic medical records",
                "FREQ-EMR", "digital_infrastructure", True, "inspection", False, None,
            ),
        ]
        for name, code, cat, mandatory, evidence, renewal, renewal_days in requirements:
            FacilityRequirementRule.objects.create(
                policy_version=pv,
                requirement_name=name,
                requirement_code=code,
                category=cat,
                mandatory=mandatory,
                evidence_type=evidence,
                renewal_required=renewal,
                renewal_interval_days=renewal_days,
                status="active",
            )
        self.stdout.write(
            f"  FH-DOC-2024-001: {len(requirements)} documentation rules"
        )

    def _seed_state_config_controls(self, pv):
        controls = [
            (
                "medical_test_minimums", "Medical Test Minimums",
                True, False, False,
            ),
            (
                "vaccination_minimums", "Vaccination Minimums",
                True, False, False,
            ),
            (
                "handler_categories", "Handler Categories",
                True, True, False,
            ),
            (
                "establishment_categories", "Establishment Categories",
                True, True, False,
            ),
            (
                "facility_approval", "Facility Approval",
                False, True, True,
            ),
            (
                "assessment_prices", "Assessment Prices",
                False, True, False,
            ),
            (
                "reporting_templates", "Reporting Templates",
                True, False, False,
            ),
            (
                "enforcement_actions", "Enforcement Actions",
                False, True, False,
            ),
            (
                "food_business_owner_obligations",
                "Food Business Owner Responsibilities",
                True, False, False,
            ),
            (
                "food_handler_hygiene", "Food Handler Hygiene Practices",
                True, False, False,
            ),
            (
                "government_oversight", "Government Regulatory Oversight",
                True, False, False,
            ),
        ]
        for domain, label, locked, editable, approval in controls:
            StateConfigurationControl.objects.create(
                policy_version=pv,
                config_domain=domain, label=label,
                federal_locked=locked,
                state_editable=editable,
                requires_federal_approval=approval,
            )
        self.stdout.write(
            f"  FH-FBO/HYGIENE/GOV-2024-001: {len(controls)} state "
            f"configuration controls"
        )

    def _seed_reporting(self, pv):
        ReportingTemplate.objects.create(
            policy_version=pv,
            template_name="Quarterly State Performance Report",
            template_code="RPT-STATE-QUARTERLY",
            reporting_frequency="quarterly",
            deadline_rule={"days_after_period_end": 15},
            required_sections=[
                "state_summary",
                "total_food_handlers_registered",
                "total_certified_food_handlers",
                "total_expired_certificates",
                "total_unfit_handlers",
                "total_approved_medical_facilities",
                "facility_reaccreditation_status",
                "vaccination_coverage",
                "illness_and_exclusion_reports",
                "enforcement_actions",
                "public_awareness_activities",
                "challenges",
                "recommendations",
                "data_quality_issues",
            ],
            required_indicators=[
                "ME-CERT-RATE", "ME-VAX-RATE", "ME-EXPIRED-RATE",
                "ME-FACILITY-ACCRED", "ME-STATE-REPORT", "ME-UNFIT-RATE",
            ],
            required_uploads=["signed_summary_letter"],
            scoring_config={
                "total_weight": 100,
                "section_weights": {
                    "state_summary": 10,
                    "data_quality_issues": 5,
                },
            },
            approval_required=True,
            status="active",
        )

        indicators = [
            (
                "Food Handler Certification Rate", "ME-CERT-RATE",
                "certificate_records", "quarterly", "card", True, "automatic", "percentage", "certificates", "FH-VALIDITY-2024-001", "",
            ),
            (
                "Vaccination Compliance Rate", "ME-VAX-RATE",
                "medical_test_records", "quarterly", "bar", True, "manual", "", "", "", "",
            ),
            (
                "Expired Certificate Rate", "ME-EXPIRED-RATE",
                "certificate_records", "monthly", "line", True, "automatic", "percentage", "certificates", "FH-VALIDITY-2024-001", "certificate_validity_months",
            ),
            (
                "Facility Accreditation Compliance", "ME-FACILITY-ACCRED",
                "facility_records", "quarterly", "bar", True, "automatic", "percentage", "medical_facilities", "FH-FAC-2024-001", "reaccreditation_interval_months",
            ),
            (
                "State Reporting Compliance", "ME-STATE-REPORT",
                "manual", "quarterly", "table", True, "manual", "", "", "", "",
            ),
            (
                "QR Verification Failure Rate", "ME-QR-FAIL",
                "inspections", "monthly", "line", False, "automatic", "percentage", "qr_verification_logs", "FH-CERT-2024-001", "requires_qr_code",
            ),
            (
                "Unfit Detection Rate", "ME-UNFIT-RATE",
                "test_results", "quarterly", "card", True, "manual", "", "", "", "",
            ),
            (
                "Return-to-Work Clearance Rate", "ME-RTW-RATE",
                "medical_test_records", "quarterly", "card", False, "hybrid", "percentage", "return_to_work_clearances", "FH-RTW-2024-001", "standard_exclusion_period_hours_after_symptoms_stop",
            ),
            (
                "Data Completeness Score", "ME-DATA-COMPLETE",
                "food_handler_registry", "quarterly", "card", True, "automatic", "percentage", "system_required_fields", "", "",
            ),
        ]
        for name, code, source, freq, viz, mandatory, input_mode, calculation_type, calculation_source, policy_standard_code, rule_parameter_key in indicators:
            MEIndicator.objects.create(
                policy_version=pv,
                indicator_name=name,
                indicator_code=code,
                data_source=source,
                reporting_frequency=freq,
                visualization_type=viz,
                input_mode=input_mode,
                calculation_type=calculation_type,
                calculation_source=calculation_source,
                policy_standard_code=policy_standard_code,
                rule_parameter_key=rule_parameter_key,
                allow_manual_override=input_mode == "hybrid",
                override_requires_reason=input_mode == "hybrid",
                mandatory=mandatory,
                federal_dashboard_visible=True,
                state_dashboard_visible=True,
                status="active",
            )
        self.stdout.write(
            f"  FH-ME-2024-001: 1 reporting template + "
            f"{len(indicators)} M&E indicators"
        )

        package = MedicalTestPackage.objects.create(
            policy_version=pv,
            name="Food Handler Medical Test Package",
            code="FH-PKG-2024-001",
            description="National minimum medical test package for food handlers (2024 Guidelines).",
            package_version="1.0",
            status="active",
        )
        T = MedicalTestPackageComponentType
        package_components = [
            (T.HEALTH_DECLARATION_FORM, "Health Declaration Form", True, False),
            (T.DOCTOR_DECLARATION_VALIDATION, "Doctor Declaration Validation", True, False),
            (T.PHYSICAL_EXAMINATION, "Physical Examination", True, False),
            (T.VACCINATION_CERTIFICATE_REVIEW, "Vaccination Certificate Review", True, False),
            (T.STOOL_MICROSCOPY_CULTURE_SENSITIVITY, "Stool microscopy, culture and sensitivity", True, False),
            (T.HEPATITIS_A_ANTIGEN, "Hepatitis A Antigen", True, False),
            (T.ADDITIONAL_TESTS, "Additional tests (if clinically indicated)", False, True),
            (T.DOCTOR_FINAL_REVIEW, "Doctor Final Review", True, False),
            (T.CERTIFICATE_OF_FITNESS, "Certificate of Fitness / Temporary Unfit Report", True, False),
        ]
        for order, (component_type, label, mandatory, conditional) in enumerate(package_components, start=1):
            MedicalTestPackageComponent.objects.create(
                package=package,
                component_type=component_type,
                label=label,
                mandatory=mandatory,
                conditional=conditional,
                order=order,
            )
        self.stdout.write(
            f"  FH-PKG-2024-001: 1 medical test package + {len(package_components)} components"
        )
