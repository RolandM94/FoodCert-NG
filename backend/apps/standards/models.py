from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class PolicyVersionStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    UNDER_REVIEW = "under_review", "Under Review"
    RETURNED = "returned", "Returned"
    APPROVED = "approved", "Approved"
    SCHEDULED = "scheduled", "Scheduled"
    ACTIVE = "active", "Active"
    RETIRED = "retired", "Retired"
    ARCHIVED = "archived", "Archived"


class PolicyVersionType(models.TextChoices):
    MAJOR = "major", "Major"
    MINOR = "minor", "Minor"
    EMERGENCY = "emergency", "Emergency"


class PolicyCategory(models.TextChoices):
    FOOD_HANDLER_ELIGIBILITY = "food_handler_eligibility", "Food Handler Eligibility Standard"
    FOOD_ESTABLISHMENT_COVERAGE = "food_establishment_coverage", "Food Establishment Coverage Standard"
    MEDICAL_TEST = "medical_test", "Medical Test Standard"
    LABORATORY_INVESTIGATION = "laboratory_investigation", "Laboratory Investigation Standard"
    VACCINATION = "vaccination", "Vaccination Standard"
    HEALTH_DECLARATION = "health_declaration", "Health Declaration Standard"
    FACILITY_ACCREDITATION = "facility_accreditation", "Facility Accreditation Standard"
    CERTIFICATE = "certificate", "Certificate Standard"
    REPORTING = "reporting", "Reporting Standard"
    COMPLIANCE_ENFORCEMENT = "compliance_enforcement", "Compliance and Enforcement Standard"
    ME_INDICATOR = "me_indicator", "M&E Indicator Standard"


class RiskLevel(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"


class StandardStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    RETIRED = "retired", "Retired"
    ARCHIVED = "archived", "Archived"


class TestType(models.TextChoices):
    LABORATORY = "laboratory", "Laboratory"
    CLINICAL = "clinical", "Clinical"
    PHYSICAL = "physical", "Physical"
    OTHER = "other", "Other"


class RuleType(models.TextChoices):
    MANDATORY = "mandatory", "Mandatory"
    CONDITIONAL = "conditional", "Conditional"
    OPTIONAL = "optional", "Optional"
    EMERGENCY = "emergency", "Emergency"


class ResultType(models.TextChoices):
    POSITIVE_NEGATIVE = "positive_negative", "Positive / Negative"
    NORMAL_ABNORMAL = "normal_abnormal", "Normal / Abnormal"
    NUMERIC = "numeric", "Numeric"
    TEXT = "text", "Text"
    FILE = "file", "File"


class Severity(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class TemplateStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    RETIRED = "retired", "Retired"


class ReportingFrequency(models.TextChoices):
    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"
    QUARTERLY = "quarterly", "Quarterly"
    BIANNUAL = "biannual", "Biannual"
    ANNUAL = "annual", "Annual"
    AD_HOC = "ad_hoc", "Ad Hoc"
    CUSTOM = "custom", "Custom"


class DataSource(models.TextChoices):
    MANUAL = "manual", "Manual"
    FOOD_HANDLER_REGISTRY = "food_handler_registry", "Food Handler Registry"
    MEDICAL_TEST_RECORDS = "medical_test_records", "Medical Test Records"
    TEST_RESULTS = "test_results", "Test Results"
    CERTIFICATE_RECORDS = "certificate_records", "Certificate Records"
    FACILITY_RECORDS = "facility_records", "Facility Records"
    FACILITY_HANDLER_MAPPING = "facility_handler_mapping", "Facility-Handler Mapping"
    TEST_CENTERS_LABS = "test_centers_labs", "Test Centers / Labs"
    INSPECTIONS = "inspections", "Inspections"
    TRAINING_ORIENTATION = "training_orientation", "Training / Orientation"
    PAYMENTS = "payments", "Payments"


class VisualizationType(models.TextChoices):
    CARD = "card", "Card"
    LINE = "line", "Line Chart"
    BAR = "bar", "Bar Chart"
    MAP = "map", "Map"
    TABLE = "table", "Table"
    PIE = "pie", "Pie Chart"


class DocumentType(models.TextChoices):
    GUIDELINE = "guideline", "National Guideline"
    SOP = "sop", "SOP"
    CIRCULAR = "circular", "Circular"
    FORM_TEMPLATE = "form_template", "Form Template"
    REPORTING_TEMPLATE = "reporting_template", "Reporting Template"
    FAQ = "faq", "FAQ"
    TRAINING = "training", "Training Material"
    AWARENESS = "awareness", "Public Awareness Material"
    MEMO = "memo", "Technical Memo"


class DocumentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    RETIRED = "retired", "Retired"
    ARCHIVED = "archived", "Archived"


class ApprovalStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RETURNED = "returned", "Returned"
    REJECTED = "rejected", "Rejected"
    APPROVED = "approved", "Approved"


class IndicatorValueStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class EvidenceApprovalStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class IndicatorValueSource(models.TextChoices):
    MANUAL = "manual", "Manual"
    AUTOMATED = "automated", "Automated"
    OVERRIDE = "override", "Override"
    IMPORT = "import", "Import"


class IndicatorDataSourceType(models.TextChoices):
    MANUAL = "manual", "Manual"
    KPI = "kpi", "KPI"
    FOOD_HANDLER_REGISTRY = "food_handler_registry", "Food Handler Registry"
    MEDICAL_TEST_RECORDS = "medical_test_records", "Medical Test Records"
    TEST_RESULTS = "test_results", "Test Results"
    CERTIFICATE_RECORDS = "certificate_records", "Certificate Records"
    FACILITY_RECORDS = "facility_records", "Facility Records"
    FACILITY_HANDLER_MAPPING = "facility_handler_mapping", "Facility-Handler Mapping"
    TEST_CENTERS_LABS = "test_centers_labs", "Test Centers / Labs"
    INSPECTIONS = "inspections", "Inspections"
    TRAINING_ORIENTATION = "training_orientation", "Training / Orientation"
    PAYMENTS = "payments", "Payments"


class IndicatorCalculationMethod(models.TextChoices):
    COUNT = "count", "Count"
    UNIQUE_COUNT = "unique_count", "Unique Count"
    SUM = "sum", "Sum"
    AVERAGE = "average", "Average"
    PERCENTAGE = "percentage", "Percentage"
    RATIO = "ratio", "Ratio"
    FORMULA = "formula", "Formula"


class IndicatorPeriodFilterMode(models.TextChoices):
    ALL_TIME = "all_time", "All Time"
    CURRENT_PERIOD = "current_period", "Current Period"
    CUSTOM_PERIOD = "custom_period", "Custom Period"


class QualitativeInputType(models.TextChoices):
    TEXT = "text", "Narrative Text"
    LIKERT_SCALE = "likert_scale", "Rating Scale"
    CATEGORY = "category", "Dropdown Category"
    RUBRIC = "rubric", "Rubric"


class KPIType(models.TextChoices):
    QUANTITATIVE = "quantitative", "Quantitative"
    QUALITATIVE = "qualitative", "Qualitative"


class KPIInputMode(models.TextChoices):
    AUTOMATIC = "automatic", "Automatic"
    MANUAL = "manual", "Manual"
    IMPORTED = "imported", "Imported"
    HYBRID = "hybrid", "Hybrid"


class KPICalculationType(models.TextChoices):
    PERCENTAGE = "percentage", "Percentage"
    COUNT = "count", "Count"
    UNIQUE_COUNT = "unique_count", "Unique Count"
    RATIO = "ratio", "Ratio"
    AVERAGE = "average", "Average"
    SUM = "sum", "Sum"
    SCORE = "score", "Score"
    FORMULA = "formula", "Formula"


class KPIRecordInputType(models.TextChoices):
    PROGRESS_ONLY = "progress_only", "Progress Only"
    CUMULATIVE_ONLY = "cumulative_only", "Cumulative Only"
    PROGRESS_OR_CUMULATIVE = "progress_or_cumulative", "Progress or Cumulative"


class KPIProgressRelationship(models.TextChoices):
    DEPENDENT = "dependent", "Dependent"
    SAME = "same", "Same"
    INDEPENDENT = "independent", "Independent"


class KPITargetDirection(models.TextChoices):
    HIGHER_BETTER = "higher_better", "Higher Is Better"
    LOWER_BETTER = "lower_better", "Lower Is Better"
    EXACT = "exact", "Exact Target"
    RANGE = "range", "Target Range"


class ImpactLevel(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    EMERGENCY = "emergency", "Emergency"


class AcknowledgementStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACKNOWLEDGED = "acknowledged", "Acknowledged"
    OVERDUE = "overdue", "Overdue"


class FacilityRequirementCategory(models.TextChoices):
    DOCUMENTATION = "documentation", "Documentation"
    STAFFING = "staffing", "Staffing"
    EQUIPMENT = "equipment", "Equipment"
    DIGITAL_INFRASTRUCTURE = "digital_infrastructure", "Digital Infrastructure"
    RECORDS = "records", "Records Management"
    CERTIFICATION = "certification", "Certificate Capability"
    REACCREDITATION = "reaccreditation", "Re-accreditation"


class EvidenceType(models.TextChoices):
    TEXT = "text", "Text"
    FILE = "file", "File Upload"
    CHECKLIST = "checklist", "Checklist"
    URL = "url", "URL"
    INSPECTION = "inspection", "Inspection"


class IndicatorCalculationStatus(models.TextChoices):
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    OVERRIDDEN = "overridden", "Overridden"


class PolicyVersion(BaseModel):
    version_code = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    version_type = models.CharField(max_length=16, choices=PolicyVersionType.choices)
    policy_category = models.CharField(
        max_length=40, choices=PolicyCategory.choices, blank=True, db_index=True,
    )
    legal_basis = models.TextField(blank=True)
    scope = models.TextField(blank=True)
    affected_entities = models.JSONField(default=list, blank=True)
    review_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=24, choices=PolicyVersionStatus.choices,
        default=PolicyVersionStatus.DRAFT, db_index=True,
    )
    effective_start_date = models.DateTimeField(null=True, blank=True)
    effective_end_date = models.DateTimeField(null=True, blank=True)
    requires_state_acknowledgement = models.BooleanField(default=True)
    change_summary = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_policy_versions",
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="submitted_policy_versions",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="approved_policy_versions",
    )
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="published_policy_versions",
    )
    retired_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="retired_policy_versions",
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    retired_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["version_code"]),
            models.Index(fields=["status", "effective_start_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.version_code} — {self.title}"


class FoodHandlerCategory(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE,
        related_name="food_handler_categories",
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64)
    description = models.TextField(blank=True, default="")
    risk_level = models.CharField(max_length=8, choices=RiskLevel.choices)
    certificate_required = models.BooleanField(default=True)
    medical_test_rule_group_id = models.UUIDField(null=True, blank=True)
    vaccination_rule_group_id = models.UUIDField(null=True, blank=True)
    nationally_locked = models.BooleanField(default=True)
    allow_state_subcategories = models.BooleanField(default=False)
    status = models.CharField(
        max_length=16, choices=StandardStatus.choices,
        default=StandardStatus.DRAFT, db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_handler_categories",
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["policy_version", "code"],
                name="unique_handler_category_code_per_version",
            ),
        ]
        indexes = [
            models.Index(fields=["policy_version", "status"]),
        ]

    def __str__(self) -> str:
        return self.name


class EstablishmentCategory(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE,
        related_name="establishment_categories",
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64)
    description = models.TextField(blank=True, default="")
    risk_level = models.CharField(max_length=8, choices=RiskLevel.choices)
    required_handler_categories = models.JSONField(default=list, blank=True)
    compliance_requirements = models.JSONField(default=list, blank=True)
    inspection_required = models.BooleanField(default=False)
    required_documents = models.JSONField(default=list, blank=True)
    allow_state_subcategories = models.BooleanField(default=False)
    status = models.CharField(
        max_length=16, choices=StandardStatus.choices,
        default=StandardStatus.DRAFT, db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_establishment_categories",
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["policy_version", "code"],
                name="unique_establishment_category_code_per_version",
            ),
        ]
        indexes = [
            models.Index(fields=["policy_version", "status"]),
        ]

    def __str__(self) -> str:
        return self.name


class MedicalTestRule(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE,
        related_name="medical_test_rules",
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64)
    test_type = models.CharField(max_length=16, choices=TestType.choices)
    rule_type = models.CharField(max_length=16, choices=RuleType.choices)
    result_type = models.CharField(
        max_length=24, choices=ResultType.choices, blank=True, default="",
    )
    accepted_values = models.JSONField(default=list, blank=True)
    blocking_values = models.JSONField(default=list, blank=True)
    blocks_certification = models.BooleanField(default=False)
    requires_attachment = models.BooleanField(default=False)
    requires_doctor_validation = models.BooleanField(default=True)
    requires_lab_validation = models.BooleanField(default=False)
    validity_days = models.IntegerField(null=True, blank=True)
    condition = models.JSONField(default=dict, blank=True, help_text="Machine-readable condition, e.g. {\"field\": \"result\", \"operator\": \"in\", \"value\": [\"positive\"]}")
    action = models.JSONField(default=dict, blank=True, help_text="Machine-readable action, e.g. {\"block_certification\": true, \"escalate\": \"doctor_review\"}")
    severity = models.CharField(max_length=16, choices=Severity.choices, blank=True, default="")
    effective_date = models.DateField(null=True, blank=True)
    applicable_categories = models.JSONField(default=list, blank=True)
    applicable_establishment_risk_levels = models.JSONField(default=list, blank=True)
    emergency_activation_rule = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=StandardStatus.choices,
        default=StandardStatus.DRAFT, db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_medical_test_rules",
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["policy_version", "code"],
                name="unique_medical_test_code_per_version",
            ),
        ]
        indexes = [
            models.Index(fields=["policy_version", "status"]),
            models.Index(fields=["rule_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_rule_type_display()})"

    def evaluate(self, value):
        """Evaluate this rule against a sample result value (rule preview/testing)."""
        reasons = []
        condition = self.condition or {}
        operator = condition.get("operator")
        target = condition.get("value")
        matched = False
        if operator == "in":
            matched = value in (target or [])
        elif operator == "not_in":
            matched = value not in (target or [])
        elif operator == "equals":
            matched = value == target
        elif operator in {"gt", "lt", "gte", "lte"}:
            try:
                numeric, threshold = float(value), float(target)
                matched = {
                    "gt": numeric > threshold,
                    "lt": numeric < threshold,
                    "gte": numeric >= threshold,
                    "lte": numeric <= threshold,
                }[operator]
            except (TypeError, ValueError):
                matched = False

        blocks = False
        if self.blocking_values and value in self.blocking_values:
            blocks = True
            reasons.append("Value is configured as a blocking value.")
        if matched and (self.action or {}).get("block_certification"):
            blocks = True
            reasons.append("Condition matched a block_certification action.")
        if matched and self.blocks_certification:
            blocks = True
            reasons.append("Condition matched and the rule blocks certification.")
        if self.accepted_values and value not in self.accepted_values and not matched:
            reasons.append("Value is not in the accepted values list.")

        return {
            "value": value,
            "matched_condition": matched,
            "blocks_certification": blocks,
            "passed": not blocks,
            "action": self.action or {},
            "reasons": reasons,
        }


class PhysicalExaminationRule(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE,
        related_name="physical_examination_rules",
    )
    indicator_name = models.CharField(max_length=255)
    code = models.CharField(max_length=64)
    description = models.TextField(blank=True, default="")
    severity = models.CharField(max_length=16, choices=Severity.choices)
    requires_doctor_notes = models.BooleanField(default=True)
    blocks_certification = models.BooleanField(default=False)
    requires_reexamination = models.BooleanField(default=False)
    requires_exclusion = models.BooleanField(default=False)
    return_to_work_rule = models.ForeignKey(
        "ReturnToWorkRule", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="physical_examination_rules",
    )
    public_health_escalation = models.BooleanField(default=False)
    status = models.CharField(
        max_length=16, choices=StandardStatus.choices,
        default=StandardStatus.DRAFT, db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_physical_exam_rules",
    )

    class Meta:
        ordering = ["indicator_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["policy_version", "code"],
                name="unique_physical_exam_code_per_version",
            ),
        ]
        indexes = [
            models.Index(fields=["policy_version", "status"]),
        ]

    def __str__(self) -> str:
        return self.indicator_name


class VaccinationRule(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE,
        related_name="vaccination_rules",
    )
    vaccine_name = models.CharField(max_length=255)
    vaccine_code = models.CharField(max_length=64)
    required = models.BooleanField(default=True)
    dose_schedule = models.JSONField(default=list, blank=True)
    validity_months = models.IntegerField(null=True, blank=True)
    grace_period_days = models.IntegerField(default=0)
    evidence_required = models.BooleanField(default=True)
    evidence_fields = models.JSONField(default=list, blank=True)
    blocks_certification_if_missing = models.BooleanField(default=False)
    blocks_certification_if_expired = models.BooleanField(default=False)
    requires_doctor_prescription_if_missing = models.BooleanField(default=True)
    applicable_categories = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=16, choices=StandardStatus.choices,
        default=StandardStatus.DRAFT, db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_vaccination_rules",
    )

    class Meta:
        ordering = ["vaccine_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["policy_version", "vaccine_code"],
                name="unique_vaccine_code_per_version",
            ),
        ]
        indexes = [
            models.Index(fields=["policy_version", "status"]),
        ]

    def __str__(self) -> str:
        return self.vaccine_name


class CertificateTemplate(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE,
        related_name="certificate_templates",
    )
    template_name = models.CharField(max_length=255)
    template_version = models.CharField(max_length=32)
    layout_config = models.JSONField(default=dict, blank=True)
    required_fields = models.JSONField(default=list, blank=True)
    certificate_number_format = models.CharField(
        max_length=128, default="FHMT-{STATE}-{YYYY}-{SEQ}",
    )
    qr_payload_config = models.JSONField(default=dict, blank=True)
    public_verification_fields = models.JSONField(default=list, blank=True)
    status_rules = models.JSONField(default=dict, blank=True)
    revocation_reasons = models.JSONField(default=list, blank=True)
    digital_signature_config = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=16, choices=TemplateStatus.choices,
        default=TemplateStatus.DRAFT, db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_standards_certificate_templates",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["policy_version", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.template_name} v{self.template_version}"


class CertificateValidityRule(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE,
        related_name="certificate_validity_rules",
    )
    routine_assessment_interval_days = models.IntegerField(default=180)
    certificate_validity_days = models.IntegerField(default=365)
    renewal_window_days = models.IntegerField(default=30)
    grace_period_days = models.IntegerField(default=0)
    expiry_reminder_days = models.JSONField(default=list, blank=True)
    illness_suspension_enabled = models.BooleanField(default=True)
    emergency_revalidation_enabled = models.BooleanField(default=False)
    status = models.CharField(
        max_length=16, choices=TemplateStatus.choices,
        default=TemplateStatus.DRAFT, db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_validity_rules",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["policy_version", "status"]),
        ]

    def __str__(self) -> str:
        return f"Validity Rule — {self.certificate_validity_days} days"


class ReturnToWorkRule(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE,
        related_name="return_to_work_rules",
    )
    condition_name = models.CharField(max_length=255)
    condition_code = models.CharField(max_length=64)
    default_exclusion_hours = models.IntegerField(default=48)
    requires_medical_clearance = models.BooleanField(default=False)
    requires_lab_clearance = models.BooleanField(default=False)
    negative_samples_required = models.IntegerField(null=True, blank=True)
    sample_interval_hours = models.IntegerField(null=True, blank=True)
    requires_health_authority_approval = models.BooleanField(default=False)
    employer_acknowledgement_required = models.BooleanField(default=False)
    clearance_document_required = models.BooleanField(default=False)
    status = models.CharField(
        max_length=16, choices=StandardStatus.choices,
        default=StandardStatus.DRAFT, db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_return_to_work_rules",
    )

    class Meta:
        ordering = ["condition_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["policy_version", "condition_code"],
                name="unique_rtw_condition_code_per_version",
            ),
        ]
        indexes = [
            models.Index(fields=["policy_version", "status"]),
        ]

    def __str__(self) -> str:
        return self.condition_name


class FacilityRequirementRule(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE,
        related_name="facility_requirement_rules",
    )
    requirement_name = models.CharField(max_length=255)
    requirement_code = models.CharField(max_length=64)
    category = models.CharField(
        max_length=32, choices=FacilityRequirementCategory.choices,
    )
    mandatory = models.BooleanField(default=True)
    evidence_type = models.CharField(
        max_length=16, choices=EvidenceType.choices, default=EvidenceType.TEXT,
    )
    renewal_required = models.BooleanField(default=False)
    renewal_interval_days = models.IntegerField(null=True, blank=True)
    suspension_trigger = models.BooleanField(default=False)
    status = models.CharField(
        max_length=16, choices=StandardStatus.choices,
        default=StandardStatus.DRAFT, db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_facility_requirements",
    )

    class Meta:
        ordering = ["category", "requirement_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["policy_version", "requirement_code"],
                name="unique_facility_req_code_per_version",
            ),
        ]
        indexes = [
            models.Index(fields=["policy_version", "status"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self) -> str:
        return f"{self.requirement_name} ({self.get_category_display()})"


class MedicalTestPackageComponentType(models.TextChoices):
    HEALTH_DECLARATION_FORM = "health_declaration_form", "Health Declaration Form"
    DOCTOR_DECLARATION_VALIDATION = "doctor_declaration_validation", "Doctor Declaration Validation"
    PHYSICAL_EXAMINATION = "physical_examination", "Physical Examination"
    VACCINATION_CERTIFICATE_REVIEW = "vaccination_certificate_review", "Vaccination Certificate Review"
    STOOL_MICROSCOPY_CULTURE_SENSITIVITY = "stool_microscopy_culture_sensitivity", "Stool Microscopy, Culture and Sensitivity"
    HEPATITIS_A_ANTIGEN = "hepatitis_a_antigen", "Hepatitis A Antigen"
    ADDITIONAL_TESTS = "additional_tests", "Additional Tests (if clinically indicated)"
    DOCTOR_FINAL_REVIEW = "doctor_final_review", "Doctor Final Review"
    CERTIFICATE_OF_FITNESS = "certificate_of_fitness", "Certificate of Fitness / Temporary Unfit Report"
    OTHER = "other", "Other"


class MedicalTestPackage(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE, related_name="medical_test_packages",
    )
    name = models.CharField(max_length=255, default="Food Handler Medical Test Package")
    code = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    package_version = models.CharField(max_length=32, default="1.0")
    status = models.CharField(
        max_length=16, choices=StandardStatus.choices,
        default=StandardStatus.DRAFT, db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_test_packages",
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["policy_version", "code"], name="unique_test_package_code_per_version"),
        ]
        indexes = [models.Index(fields=["policy_version", "status"])]

    def __str__(self) -> str:
        return f"{self.name} v{self.package_version}"


class MedicalTestPackageComponent(BaseModel):
    package = models.ForeignKey(MedicalTestPackage, on_delete=models.CASCADE, related_name="components")
    component_type = models.CharField(max_length=48, choices=MedicalTestPackageComponentType.choices)
    label = models.CharField(max_length=255)
    mandatory = models.BooleanField(default=True)
    conditional = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["order", "label"]
        constraints = [
            models.UniqueConstraint(fields=["package", "component_type"], name="unique_component_type_per_package"),
        ]

    def __str__(self) -> str:
        return f"{self.label} ({'mandatory' if self.mandatory else 'optional'})"


class ReportingTemplate(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE,
        related_name="reporting_templates",
    )
    template_name = models.CharField(max_length=255)
    template_code = models.CharField(max_length=64)
    reporting_frequency = models.CharField(
        max_length=16, choices=ReportingFrequency.choices,
    )
    deadline_rule = models.JSONField(default=dict, blank=True)
    required_sections = models.JSONField(default=list, blank=True)
    required_indicators = models.JSONField(default=list, blank=True)
    required_uploads = models.JSONField(default=list, blank=True)
    scoring_config = models.JSONField(default=dict, blank=True)
    approval_required = models.BooleanField(default=True)
    status = models.CharField(
        max_length=16, choices=TemplateStatus.choices,
        default=TemplateStatus.DRAFT, db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_reporting_templates",
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["policy_version", "template_code"],
                name="unique_reporting_template_code_per_version",
            ),
        ]
        indexes = [
            models.Index(fields=["policy_version", "status"]),
        ]

    def __str__(self) -> str:
        return self.template_name


class IndicatorOwnerType(models.TextChoices):
    FEDERAL = "federal", "Federal-Owned"
    STATE = "state", "State-Owned"
    SYSTEM = "system", "System Indicator"
    EMPLOYER = "employer", "Employer-Scoped"
    FACILITY = "facility", "Facility-Scoped"


class IndicatorVisibility(models.TextChoices):
    SYSTEM_DEFAULT = "system_default", "System Default"
    FEDERAL_PRIVATE = "federal_private", "Federal Private"
    FEDERAL_STANDARD = "federal_standard", "Federal Standard"
    FEDERAL_SHARED = "federal_shared", "Federal Shared"
    STATE_OWNED = "state_owned", "State Owned"
    STATE_PRIVATE = "state_private", "State Private"
    ORGANIZATION_SCOPED = "organization_scoped", "Organization Scoped"
    ROLE_SCOPED = "role_scoped", "Role Scoped"


class IndicatorLifecycleStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    UNDER_REVIEW = "under_review", "Under Review"
    PUBLISHED = "published", "Published"
    ACTIVE = "active", "Active"
    PAUSED = "paused", "Paused"
    DEPRECATED = "deprecated", "Deprecated"
    ARCHIVED = "archived", "Archived"


class MEIndicator(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE,
        related_name="me_indicators",
    )
    indicator_name = models.CharField(max_length=255)
    indicator_code = models.CharField(max_length=64)
    description = models.TextField(blank=True, default="")
    kpi_type = models.CharField(
        max_length=16, choices=KPIType.choices,
        default=KPIType.QUANTITATIVE,
    )
    unit_of_measurement = models.CharField(max_length=64, blank=True, default="count")
    input_mode = models.CharField(
        max_length=16, choices=KPIInputMode.choices,
        default=KPIInputMode.MANUAL,
    )
    record_input_type = models.CharField(
        max_length=32, choices=KPIRecordInputType.choices,
        default=KPIRecordInputType.PROGRESS_ONLY,
    )
    progress_cumulative_relationship = models.CharField(
        max_length=32, choices=KPIProgressRelationship.choices,
        default=KPIProgressRelationship.DEPENDENT,
    )
    target_direction = models.CharField(
        max_length=24, choices=KPITargetDirection.choices,
        default=KPITargetDirection.HIGHER_BETTER,
    )
    calculation_type = models.CharField(
        max_length=16, choices=KPICalculationType.choices,
        blank=True, default="",
    )
    calculation_source = models.CharField(max_length=64, blank=True, default="")
    numerator_definition = models.JSONField(default=dict, blank=True)
    denominator_definition = models.JSONField(default=dict, blank=True)
    policy_standard_code = models.CharField(max_length=64, blank=True, default="")
    rule_parameter_key = models.CharField(max_length=128, blank=True, default="")
    allow_manual_override = models.BooleanField(default=False)
    override_requires_reason = models.BooleanField(default=False)
    last_calculated_at = models.DateTimeField(null=True, blank=True)
    latest_value = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True,
    )
    achievement_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    visibility_scope = models.JSONField(default=dict, blank=True)
    formula_config = models.JSONField(default=dict, blank=True)
    data_source = models.CharField(max_length=32, choices=DataSource.choices)
    reporting_frequency = models.CharField(
        max_length=16, choices=ReportingFrequency.choices,
    )
    target_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    threshold_config = models.JSONField(default=dict, blank=True)
    visualization_type = models.CharField(
        max_length=8, choices=VisualizationType.choices, default=VisualizationType.CARD,
    )
    federal_dashboard_visible = models.BooleanField(default=True)
    state_dashboard_visible = models.BooleanField(default=True)
    mandatory = models.BooleanField(default=False)
    status = models.CharField(
        max_length=16, choices=StandardStatus.choices,
        default=StandardStatus.DRAFT, db_index=True,
    )
    # --- Performance Indicators layer (PRD) ---
    category = models.CharField(max_length=120, blank=True, default="", db_index=True)
    owner_type = models.CharField(max_length=16, choices=IndicatorOwnerType.choices, default=IndicatorOwnerType.FEDERAL, db_index=True)
    owner_organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="owned_indicators",
    )
    owner_state = models.ForeignKey(
        "locations.State", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="owned_indicators",
    )
    visibility = models.CharField(max_length=24, choices=IndicatorVisibility.choices, default=IndicatorVisibility.FEDERAL_PRIVATE, db_index=True)
    account_type_scope = models.JSONField(default=list, blank=True)
    lifecycle_status = models.CharField(max_length=16, choices=IndicatorLifecycleStatus.choices, default=IndicatorLifecycleStatus.DRAFT, db_index=True)
    version = models.CharField(max_length=32, blank=True, default="1.0")
    privacy_classification = models.CharField(max_length=32, blank=True, default="internal")
    allow_state_target_override = models.BooleanField(default=True)
    allow_state_clone = models.BooleanField(default=True)
    dashboard_enabled = models.BooleanField(default=True)
    report_enabled = models.BooleanField(default=True)
    ai_enabled = models.BooleanField(default=True)
    source_indicator = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="cloned_indicators",
        help_text="Federal indicator this state indicator was cloned from",
    )
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="published_me_indicators",
    )
    published_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="updated_me_indicators",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_me_indicators",
    )

    class Meta:
        ordering = ["indicator_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["policy_version", "indicator_code"],
                name="unique_me_indicator_code_per_version",
            ),
        ]
        indexes = [
            models.Index(fields=["policy_version", "status"]),
            models.Index(fields=["data_source"]),
            models.Index(fields=["owner_type", "lifecycle_status"]),
            models.Index(fields=["visibility"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self) -> str:
        return self.indicator_name


class IndicatorScopeType(models.TextChoices):
    NATIONAL = "national", "National"
    FEDERAL = "federal", "Federal"
    STATE = "state", "State"
    LGA = "lga", "LGA"
    EMPLOYER = "employer", "Employer"
    FACILITY = "facility", "Facility"
    BRANCH = "branch", "Branch"
    CUSTOM = "custom", "Custom"


class IndicatorTargetSource(models.TextChoices):
    FEDERAL_DEFAULT = "federal_default", "Federal Default"
    STATE_OVERRIDE = "state_override", "State Override"
    LGA = "lga", "LGA"
    ORGANIZATION = "organization", "Organization"
    CUSTOM = "custom", "Custom"


class IndicatorTarget(BaseModel):
    indicator = models.ForeignKey(MEIndicator, on_delete=models.CASCADE, related_name="targets")
    scope_type = models.CharField(max_length=16, choices=IndicatorScopeType.choices, default=IndicatorScopeType.NATIONAL, db_index=True)
    scope_id = models.CharField(max_length=64, blank=True, default="")
    target_value = models.DecimalField(max_digits=18, decimal_places=4)
    target_unit = models.CharField(max_length=64, blank=True, default="")
    effective_start_date = models.DateField(null=True, blank=True)
    effective_end_date = models.DateField(null=True, blank=True)
    set_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="set_indicator_targets")
    source = models.CharField(max_length=24, choices=IndicatorTargetSource.choices, default=IndicatorTargetSource.FEDERAL_DEFAULT)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["indicator__indicator_name", "scope_type", "scope_id"]
        indexes = [
            models.Index(fields=["indicator", "scope_type", "scope_id"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.indicator.indicator_code} target [{self.scope_type}:{self.scope_id or 'all'}] = {self.target_value}"


class IndicatorThresholdSeverity(models.TextChoices):
    GOOD = "good", "Good"
    WARNING = "warning", "Warning"
    CRITICAL = "critical", "Critical"


class IndicatorThreshold(BaseModel):
    indicator = models.ForeignKey(MEIndicator, on_delete=models.CASCADE, related_name="thresholds")
    scope_type = models.CharField(max_length=16, choices=IndicatorScopeType.choices, default=IndicatorScopeType.NATIONAL, db_index=True)
    scope_id = models.CharField(max_length=64, blank=True, default="")
    band_name = models.CharField(max_length=64)
    severity = models.CharField(max_length=16, choices=IndicatorThresholdSeverity.choices, default=IndicatorThresholdSeverity.GOOD)
    min_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    max_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    color = models.CharField(max_length=24, blank=True, default="")
    label = models.CharField(max_length=120, blank=True, default="")
    action_recommendation = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["indicator__indicator_name", "scope_type", "min_value"]
        indexes = [
            models.Index(fields=["indicator", "scope_type", "scope_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.indicator.indicator_code} band {self.band_name} ({self.severity})"


class IndicatorAdoptionStatus(models.TextChoices):
    AVAILABLE = "available", "Available"
    ADOPTED = "adopted", "Adopted"
    CLONED = "cloned", "Cloned"
    DECLINED = "declined", "Declined"
    SUPERSEDED = "superseded", "Superseded"


class IndicatorAdoption(BaseModel):
    federal_indicator = models.ForeignKey(MEIndicator, on_delete=models.CASCADE, related_name="adoptions")
    state = models.ForeignKey("locations.State", on_delete=models.CASCADE, related_name="indicator_adoptions")
    adoption_status = models.CharField(max_length=16, choices=IndicatorAdoptionStatus.choices, default=IndicatorAdoptionStatus.ADOPTED, db_index=True)
    adopted_version = models.CharField(max_length=32, blank=True, default="")
    state_target_override_enabled = models.BooleanField(default=False)
    cloned_indicator = models.ForeignKey(
        MEIndicator, on_delete=models.SET_NULL, null=True, blank=True, related_name="clone_adoption",
    )
    adopted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="indicator_adoptions")
    adopted_at = models.DateTimeField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-adopted_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["federal_indicator", "state"], name="unique_indicator_adoption_per_state"),
        ]
        indexes = [
            models.Index(fields=["state", "adoption_status"]),
        ]

    def __str__(self) -> str:
        return f"{self.federal_indicator.indicator_code} -> {self.state.name} ({self.adoption_status})"


class IndicatorManualEntryReviewStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class IndicatorManualEntry(BaseModel):
    indicator = models.ForeignKey(MEIndicator, on_delete=models.CASCADE, related_name="manual_entries")
    scope_type = models.CharField(max_length=16, choices=IndicatorScopeType.choices, default=IndicatorScopeType.NATIONAL)
    scope_id = models.CharField(max_length=64, blank=True, default="")
    period_start = models.DateField()
    period_end = models.DateField()
    value = models.DecimalField(max_digits=18, decimal_places=4)
    evidence_file_url = models.URLField(blank=True, default="")
    comment = models.TextField(blank=True, default="")
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="submitted_indicator_manual_entries")
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_indicator_manual_entries")
    review_status = models.CharField(max_length=16, choices=IndicatorManualEntryReviewStatus.choices, default=IndicatorManualEntryReviewStatus.DRAFT, db_index=True)
    review_comment = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-period_end", "-created_at"]
        indexes = [
            models.Index(fields=["indicator", "review_status"]),
            models.Index(fields=["period_start", "period_end"]),
        ]

    def __str__(self) -> str:
        return f"{self.indicator.indicator_code} manual {self.period_end} ({self.review_status})"


class MEIndicatorDataSource(BaseModel):
    indicator = models.ForeignKey(
        MEIndicator, on_delete=models.CASCADE,
        related_name="data_source_configs",
    )
    source_type = models.CharField(
        max_length=32, choices=IndicatorDataSourceType.choices,
        default=IndicatorDataSourceType.MANUAL,
    )
    source_id = models.CharField(max_length=128, blank=True, default="")
    calculation_method = models.CharField(
        max_length=16, choices=IndicatorCalculationMethod.choices,
    )
    value_field_id = models.CharField(max_length=128, blank=True, default="")
    numerator_config_json = models.JSONField(default=dict, blank=True)
    denominator_config_json = models.JSONField(default=dict, blank=True)
    filter_config_json = models.JSONField(default=dict, blank=True)
    unicity_field_id = models.CharField(max_length=128, blank=True, default="")
    period_filter_mode = models.CharField(
        max_length=16, choices=IndicatorPeriodFilterMode.choices,
        default=IndicatorPeriodFilterMode.CURRENT_PERIOD,
    )

    class Meta:
        ordering = ["indicator__indicator_name", "source_type", "calculation_method"]
        indexes = [
            models.Index(fields=["indicator", "source_type"]),
            models.Index(fields=["calculation_method"]),
            models.Index(fields=["period_filter_mode"]),
        ]

    def __str__(self) -> str:
        return f"{self.indicator.indicator_code} {self.source_type} {self.calculation_method}"


class QualitativeIndicatorConfig(BaseModel):
    indicator = models.OneToOneField(
        MEIndicator, on_delete=models.CASCADE,
        related_name="qualitative_config",
    )
    input_type = models.CharField(
        max_length=16, choices=QualitativeInputType.choices,
        default=QualitativeInputType.TEXT,
    )
    scale_min = models.IntegerField(null=True, blank=True)
    scale_max = models.IntegerField(null=True, blank=True)
    scale_labels_json = models.JSONField(default=dict, blank=True)
    category_options_json = models.JSONField(default=list, blank=True)
    requires_narrative = models.BooleanField(default=False)

    class Meta:
        ordering = ["indicator__indicator_name"]
        indexes = [
            models.Index(fields=["input_type"]),
            models.Index(fields=["requires_narrative"]),
        ]

    def __str__(self) -> str:
        return f"{self.indicator.indicator_code} {self.input_type}"


class IndicatorDisaggregation(BaseModel):
    indicator = models.ForeignKey(
        MEIndicator, on_delete=models.CASCADE,
        related_name="disaggregations",
    )
    source_type = models.CharField(
        max_length=32, choices=IndicatorDataSourceType.choices,
        default=IndicatorDataSourceType.MANUAL,
    )
    field_id = models.CharField(max_length=128)
    field_label = models.CharField(max_length=255)
    level = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["indicator__indicator_name", "level", "field_label"]
        constraints = [
            models.UniqueConstraint(
                fields=["indicator", "field_id"],
                name="unique_indicator_disaggregation_field",
            ),
            models.UniqueConstraint(
                fields=["indicator", "level"],
                name="unique_indicator_disaggregation_level",
            ),
        ]
        indexes = [
            models.Index(fields=["indicator", "source_type"]),
            models.Index(fields=["indicator", "level"]),
        ]

    def __str__(self) -> str:
        return f"{self.indicator.indicator_code} {self.field_label}"


class MEIndicatorValue(BaseModel):
    indicator = models.ForeignKey(
        MEIndicator, on_delete=models.CASCADE,
        related_name="values",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    progress_value_numeric = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True,
    )
    cumulative_value_numeric = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True,
    )
    qualitative_value_text = models.TextField(blank=True, default="")
    qualitative_rating = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
    )
    qualitative_category = models.CharField(max_length=128, blank=True, default="")
    value_source = models.CharField(
        max_length=16, choices=IndicatorValueSource.choices,
        default=IndicatorValueSource.MANUAL,
    )
    source_reference_id = models.CharField(max_length=128, blank=True, default="")
    approval_status = models.CharField(
        max_length=16, choices=IndicatorValueStatus.choices,
        default=IndicatorValueStatus.DRAFT, db_index=True,
    )
    target_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    variance_from_target = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    performance_band = models.CharField(max_length=64, blank=True, default="")
    performance_severity = models.CharField(max_length=16, blank=True, default="")
    calculation_snapshot_json = models.JSONField(default=dict, blank=True)
    original_calculated_value = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True,
    )
    overridden_value = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True,
    )
    override_reason = models.TextField(blank=True, default="")
    overridden_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="overridden_me_indicator_values",
    )
    overridden_at = models.DateTimeField(null=True, blank=True)
    evidence_json = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True, default="")
    rejection_comment = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_me_indicator_values",
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="submitted_me_indicator_values",
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="approved_me_indicator_values",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-period_end", "indicator__indicator_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["indicator", "period_start", "period_end", "value_source", "source_reference_id"],
                name="unique_me_indicator_value_per_source_period",
            ),
        ]
        indexes = [
            models.Index(fields=["indicator", "period_start", "period_end"]),
            models.Index(fields=["approval_status"]),
            models.Index(fields=["value_source"]),
        ]

    def __str__(self) -> str:
        return f"{self.indicator.indicator_code} {self.period_start} - {self.period_end}"


class IndicatorDisaggregatedValue(BaseModel):
    indicator_value = models.ForeignKey(
        MEIndicatorValue, on_delete=models.CASCADE,
        related_name="disaggregated_values",
    )
    indicator = models.ForeignKey(
        MEIndicator, on_delete=models.CASCADE,
        related_name="disaggregated_values",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    dimension_values_json = models.JSONField(default=dict, blank=True)
    value_numeric = models.DecimalField(max_digits=18, decimal_places=4)

    class Meta:
        ordering = ["indicator__indicator_name", "period_start", "dimension_values_json"]
        indexes = [
            models.Index(fields=["indicator", "period_start", "period_end"]),
            models.Index(fields=["indicator_value"]),
        ]

    def __str__(self) -> str:
        return f"{self.indicator.indicator_code} {self.dimension_values_json}"


class IndicatorEvidence(BaseModel):
    indicator = models.ForeignKey(
        MEIndicator, on_delete=models.CASCADE,
        related_name="evidence",
    )
    indicator_value = models.ForeignKey(
        MEIndicatorValue, on_delete=models.CASCADE,
        null=True, blank=True, related_name="evidence_items",
    )
    document_id = models.CharField(max_length=128, blank=True, default="")
    file_id = models.CharField(max_length=128, blank=True, default="")
    file_url = models.CharField(max_length=512, blank=True, default="")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    evidence_type = models.CharField(
        max_length=16, choices=EvidenceType.choices,
        default=EvidenceType.TEXT,
    )
    approval_status = models.CharField(
        max_length=16, choices=EvidenceApprovalStatus.choices,
        default=EvidenceApprovalStatus.DRAFT, db_index=True,
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="uploaded_indicator_evidence",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="approved_indicator_evidence",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_comment = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["indicator", "approval_status"]),
            models.Index(fields=["indicator_value", "approval_status"]),
            models.Index(fields=["evidence_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.indicator.indicator_code} {self.title}"


class MEIndicatorValueHistory(BaseModel):
    value = models.ForeignKey(
        MEIndicatorValue, on_delete=models.CASCADE,
        related_name="history",
    )
    action = models.CharField(max_length=32)
    from_status = models.CharField(max_length=16, blank=True, default="")
    to_status = models.CharField(max_length=16, blank=True, default="")
    snapshot_json = models.JSONField(default=dict, blank=True)
    comment = models.TextField(blank=True, default="")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="me_indicator_value_history",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["value", "created_at"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self) -> str:
        return f"{self.value_id} {self.action}"


class MEIndicatorCalculationLog(BaseModel):
    indicator = models.ForeignKey(
        MEIndicator, on_delete=models.CASCADE,
        related_name="calculation_logs",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    calculated_value = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True,
    )
    numerator_value = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True,
    )
    denominator_value = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True,
    )
    filters_used = models.JSONField(default=dict, blank=True)
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="indicator_calculation_logs",
    )
    policy_standard_code = models.CharField(max_length=64, blank=True, default="")
    policy_standard_id = models.CharField(max_length=128, blank=True, default="")
    calculated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="me_indicator_calculation_logs",
    )
    calculation_status = models.CharField(
        max_length=16, choices=IndicatorCalculationStatus.choices,
        default=IndicatorCalculationStatus.SUCCESS, db_index=True,
    )
    error_message = models.TextField(blank=True, default="")
    source_record_count = models.PositiveIntegerField(default=0)
    snapshot_json = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["indicator", "period_start", "period_end"]),
            models.Index(fields=["calculation_status"]),
            models.Index(fields=["policy_version"]),
        ]

    def __str__(self) -> str:
        return f"{self.indicator.indicator_code} {self.period_start} - {self.period_end}"


class PolicyDocument(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="policy_documents",
    )
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=24, choices=DocumentType.choices)
    description = models.TextField(blank=True, default="")
    file_url = models.CharField(max_length=512)
    version_label = models.CharField(max_length=64)
    target_audience = models.JSONField(default=list, blank=True)
    requires_acknowledgement = models.BooleanField(default=False)
    status = models.CharField(
        max_length=16, choices=DocumentStatus.choices,
        default=DocumentStatus.DRAFT, db_index=True,
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="uploaded_policy_documents",
    )
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="published_policy_documents",
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["document_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.version_label})"


class Approval(BaseModel):
    entity_type = models.CharField(max_length=64, db_index=True)
    entity_id = models.UUIDField(db_index=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="standards_approval_requests",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="standards_approval_reviews",
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="standards_approvals",
    )
    status = models.CharField(
        max_length=16, choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING, db_index=True,
    )
    impact_level = models.CharField(
        max_length=16, choices=ImpactLevel.choices, default=ImpactLevel.MEDIUM,
    )
    request_comment = models.TextField(blank=True, default="")
    review_comment = models.TextField(blank=True, default="")
    approval_comment = models.TextField(blank=True, default="")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Approval {self.entity_type}:{self.entity_id} — {self.status}"


class StateAcknowledgement(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE,
        related_name="state_acknowledgements",
    )
    state = models.ForeignKey(
        "locations.State", on_delete=models.CASCADE,
        related_name="policy_acknowledgements",
    )
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="policy_acknowledgements",
    )
    acknowledgement_comment = models.TextField(blank=True, default="")
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=AcknowledgementStatus.choices,
        default=AcknowledgementStatus.PENDING, db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["policy_version", "state"],
                name="unique_acknowledgement_per_state_version",
            ),
        ]
        indexes = [
            models.Index(fields=["policy_version", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.state} — {self.policy_version.version_code}"


class StateConfigurationControl(BaseModel):
    policy_version = models.ForeignKey(
        PolicyVersion, on_delete=models.CASCADE,
        related_name="state_configuration_controls",
    )
    config_domain = models.CharField(max_length=64, db_index=True)
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    federal_locked = models.BooleanField(default=True)
    state_editable = models.BooleanField(default=False)
    requires_federal_approval = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="created_state_config_controls",
    )

    class Meta:
        ordering = ["config_domain", "label"]
        constraints = [
            models.UniqueConstraint(
                fields=["policy_version", "config_domain"],
                name="unique_state_config_domain_per_version",
            ),
        ]
        indexes = [
            models.Index(fields=["policy_version"]),
        ]

    def __str__(self) -> str:
        return f"{self.label} ({'Locked' if self.federal_locked else 'Editable'})"
