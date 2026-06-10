from django.db import models

from apps.common.models import UUIDModel, TimestampedModel
from apps.accounts.models import User
from apps.organizations.models import Organization, OrganizationUnit


class FormTemplatePurpose(models.TextChoices):
    INSPECTION_CHECKLIST = "inspection_checklist", "Inspection Checklist"
    EMPLOYER_DATA_COLLECTION = "employer_data_collection", "Employer Data Collection"
    EMPLOYER_COMPLIANCE = "employer_compliance", "Employer Compliance Self-Assessment"
    FACILITY_DATA_COLLECTION = "facility_data_collection", "Medical Facility Data Collection"
    FACILITY_MONTHLY_REPORT = "facility_monthly_report", "Medical Facility Monthly Report"
    ACCREDITATION_CHECKLIST = "accreditation_checklist", "Accreditation Checklist"
    RE_ACCREDITATION_CHECKLIST = "re_accreditation_checklist", "Re-accreditation Checklist"
    FOOD_HANDLER_SURVEY = "food_handler_survey", "Food Handler Survey"
    FOOD_HANDLER_DECLARATION = "food_handler_declaration", "Food Handler Declaration"
    INCIDENT_REPORT = "incident_report", "Incident Report"
    TRAINING_FEEDBACK = "training_feedback", "Training Feedback"
    GENERAL_DATA_COLLECTION = "general_data_collection", "General Data Collection"


class FormTemplateStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"
    DEPRECATED = "deprecated", "Deprecated"


class FormTemplate(UUIDModel, TimestampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    purpose = models.CharField(max_length=50, choices=FormTemplatePurpose.choices, db_index=True)
    owner_organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="form_templates")
    target_respondent_type = models.CharField(max_length=50, blank=True)
    module_context = models.CharField(max_length=50, blank=True, help_text="e.g. inspections, employer, facility, food_handler")
    status = models.CharField(max_length=20, choices=FormTemplateStatus.choices, default=FormTemplateStatus.DRAFT, db_index=True)
    current_version = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="form_templates_created")

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["purpose"]),
            models.Index(fields=["status"]),
            models.Index(fields=["owner_organization"]),
        ]

    def __str__(self):
        return f"{self.title} v{self.current_version}"


class FormTemplateVersion(UUIDModel, TimestampedModel):
    template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    schema_json = models.JSONField(default=dict, help_text="Sections and questions definition")
    scoring_json = models.JSONField(default=dict, blank=True)
    conditional_logic_json = models.JSONField(default=dict, blank=True)
    published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="template_versions_published")
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=FormTemplateStatus.choices, default=FormTemplateStatus.DRAFT)

    class Meta:
        unique_together = [("template", "version_number")]
        ordering = ["-version_number"]

    def __str__(self):
        return f"{self.template.title} v{self.version_number}"


class AssignmentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SCHEDULED = "scheduled", "Scheduled"
    ACTIVE = "active", "Active"
    IN_PROGRESS = "in_progress", "In Progress"
    SUBMITTED = "submitted", "Submitted"
    RETURNED = "returned", "Returned"
    REVIEWED = "reviewed", "Reviewed"
    OVERDUE = "overdue", "Overdue"
    CANCELLED = "cancelled", "Cancelled"
    CLOSED = "closed", "Closed"


class FormAssignment(UUIDModel, TimestampedModel):
    title = models.CharField(max_length=255)
    template = models.ForeignKey(FormTemplate, on_delete=models.PROTECT, related_name="assignments")
    template_version = models.ForeignKey(FormTemplateVersion, on_delete=models.PROTECT, null=True, related_name="assignments")
    purpose = models.CharField(max_length=50, choices=FormTemplatePurpose.choices)
    assigned_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="assignments_created")
    assigned_to_type = models.CharField(max_length=50, help_text="user, organization, unit, role, group")
    assigned_to_id = models.CharField(max_length=100, blank=True)
    recipient_role = models.CharField(max_length=50, blank=True)
    context_type = models.CharField(max_length=50, blank=True, help_text="inspection, employer, facility, accreditation, general")
    context_id = models.CharField(max_length=100, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    allow_draft = models.BooleanField(default=True)
    allow_multiple_submissions = models.BooleanField(default=False)
    allow_late_submission = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)
    reviewer_role = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.DRAFT, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["purpose"]),
            models.Index(fields=["assigned_to_type"]),
            models.Index(fields=["context_type"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"


class ResponseStatus(models.TextChoices):
    NOT_STARTED = "not_started", "Not Started"
    IN_PROGRESS = "in_progress", "In Progress"
    SUBMITTED = "submitted", "Submitted"
    RETURNED = "returned", "Returned"
    REVIEWED = "reviewed", "Reviewed"
    OVERDUE = "overdue", "Overdue"
    CANCELLED = "cancelled", "Cancelled"


class FormResponse(UUIDModel, TimestampedModel):
    assignment = models.ForeignKey(FormAssignment, on_delete=models.CASCADE, related_name="responses")
    template = models.ForeignKey(FormTemplate, on_delete=models.PROTECT, related_name="responses")
    template_version = models.ForeignKey(FormTemplateVersion, on_delete=models.PROTECT, null=True, related_name="responses")
    respondent_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="form_responses")
    respondent_organization = models.ForeignKey(Organization, on_delete=models.PROTECT, null=True, blank=True, related_name="form_responses")
    context_type = models.CharField(max_length=50, blank=True)
    context_id = models.CharField(max_length=100, blank=True)
    response_json = models.JSONField(default=dict)
    score = models.FloatField(null=True, blank=True)
    risk_rating = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=ResponseStatus.choices, default=ResponseStatus.NOT_STARTED, db_index=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="responses_reviewed")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    returned_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["assignment"]),
            models.Index(fields=["respondent_user"]),
        ]

    def __str__(self):
        return f"Response by {self.respondent_user} for {self.template.title}"
