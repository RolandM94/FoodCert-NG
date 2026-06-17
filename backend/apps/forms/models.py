from django.db import models
from django.utils import timezone

from apps.common.models import UUIDModel, TimestampedModel
from apps.accounts.models import User
from apps.organizations.models import Organization


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
    NATIONAL_POLICY_TEMPLATE = "national_policy_template", "National Policy Template"
    STATE_REPORTING_FORM = "state_reporting_form", "State Reporting Form"
    FEDERAL_ME_DATA_COLLECTION = "federal_me_data_collection", "Federal M&E Data Collection"
    FEDERAL_COMPLIANCE_REVIEW = "federal_compliance_review", "Federal Compliance Review"
    NATIONAL_INCIDENT_REPORTING = "national_incident_reporting", "National Incident Reporting"
    PROGRAMME_MONITORING_FORM = "programme_monitoring_form", "Programme Monitoring Form"
    GUIDELINE_IMPLEMENTATION_SURVEY = "guideline_implementation_survey", "Guideline Implementation Survey"
    CROSS_STATE_SURVEY = "cross_state_survey", "Cross-State Survey"
    NATIONAL_FACILITY_REPORTING_TEMPLATE = "national_facility_reporting_template", "National Facility Reporting Template"
    INSPECTION_PERFORMANCE_REPORTING_TEMPLATE = "inspection_performance_reporting_template", "Inspection Performance Reporting Template"


class FormPrimaryModule(models.TextChoices):
    INSPECTIONS = "inspections", "Inspections"
    EMPLOYERS = "employers", "Employers / Food Businesses"
    FACILITIES = "facilities", "Medical Facilities"
    ACCREDITATION = "accreditation", "Accreditation"
    FOOD_HANDLERS = "food_handlers", "Food Handlers"
    REPORTS = "reports", "Reports"
    COMPLIANCE = "compliance", "Compliance Monitoring"
    TRAINING = "training", "Training / Feedback"
    INCIDENTS = "incidents", "Incident Reporting"
    GENERAL = "general", "General"


class FormTemplateStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"
    DEPRECATED = "deprecated", "Deprecated"


class FormTemplateVisibility(models.TextChoices):
    STATE_OWNED = "state_owned", "State Owned"
    FEDERAL_PRIVATE = "federal_private", "Federal Private"
    FEDERAL_SHARED = "federal_shared", "Federal Shared"
    FEDERAL_STANDARD = "federal_standard", "Federal Standard"


class FormVersionStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    DEPRECATED = "deprecated", "Deprecated"


class FormRecipientStatus(models.TextChoices):
    NOT_STARTED = "not_started", "Not Started"
    IN_PROGRESS = "in_progress", "In Progress"
    SUBMITTED = "submitted", "Submitted"
    REVIEWED = "reviewed", "Reviewed"
    RETURNED = "returned", "Returned"
    OVERDUE = "overdue", "Overdue"
    CANCELLED = "cancelled", "Cancelled"


class FormSyncStatus(models.TextChoices):
    ONLINE = "online", "Online"
    AVAILABLE_OFFLINE = "available_offline", "Available Offline"
    SYNC_PENDING = "sync_pending", "Sync Pending"
    SYNCING = "syncing", "Syncing"
    SYNCED = "synced", "Synced"
    SYNC_FAILED = "sync_failed", "Sync Failed"
    CONFLICT = "conflict", "Conflict Detected"


class FormTemplate(UUIDModel, TimestampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    purpose = models.CharField(max_length=50, choices=FormTemplatePurpose.choices, db_index=True)
    owner_organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="form_templates")
    target_respondent_type = models.CharField(max_length=50, blank=True)
    primary_module = models.CharField(max_length=50, choices=FormPrimaryModule.choices, default=FormPrimaryModule.GENERAL, db_index=True)
    module_context = models.CharField(max_length=50, blank=True, help_text="Compatibility field; use primary_module for new forms.")
    default_context_type = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=16, default="en")
    settings_json = models.JSONField(default=dict, blank=True)
    visibility = models.CharField(
        max_length=32,
        choices=FormTemplateVisibility.choices,
        default=FormTemplateVisibility.STATE_OWNED,
        db_index=True,
    )
    shared_with_states = models.ManyToManyField(
        "locations.State",
        blank=True,
        related_name="shared_form_templates",
    )
    source_template = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derived_templates",
    )
    source_version = models.ForeignKey(
        "FormTemplateVersion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derived_templates",
    )
    status = models.CharField(max_length=20, choices=FormTemplateStatus.choices, default=FormTemplateStatus.DRAFT, db_index=True)
    current_version = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="form_templates_created")
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["purpose"]),
            models.Index(fields=["status"]),
            models.Index(fields=["owner_organization"]),
            models.Index(fields=["primary_module", "status"]),
            models.Index(fields=["visibility", "status"]),
        ]

    def __str__(self):
        return f"{self.title} v{self.current_version}"


class FormTemplateVersion(UUIDModel, TimestampedModel):
    template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    schema_json = models.JSONField(default=dict, help_text="Sections and questions definition")
    logic_json = models.JSONField(default=dict, blank=True)
    scoring_json = models.JSONField(default=dict, blank=True)
    conditional_logic_json = models.JSONField(default=dict, blank=True)
    settings_json = models.JSONField(default=dict, blank=True)
    published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="template_versions_published")
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=FormVersionStatus.choices, default=FormVersionStatus.DRAFT)

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
    allow_offline = models.BooleanField(default=False)
    allow_multiple_submissions = models.BooleanField(default=False)
    allow_late_submission = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)
    reviewer_role = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.DRAFT, db_index=True)
    closed_at = models.DateTimeField(null=True, blank=True)

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
    DRAFT = "draft", "Draft"
    IN_PROGRESS = "in_progress", "In Progress"
    SUBMITTED = "submitted", "Submitted"
    RETURNED = "returned", "Returned"
    REVIEWED = "reviewed", "Reviewed"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    OVERDUE = "overdue", "Overdue"
    CANCELLED = "cancelled", "Cancelled"
    SYNC_PENDING = "sync_pending", "Sync Pending"
    SYNC_FAILED = "sync_failed", "Sync Failed"


class FormRecipient(UUIDModel, TimestampedModel):
    assignment = models.ForeignKey(FormAssignment, on_delete=models.CASCADE, related_name="recipients")
    recipient_type = models.CharField(max_length=50)
    recipient_id = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, null=True, blank=True, related_name="form_recipients")
    role_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=FormRecipientStatus.choices, default=FormRecipientStatus.NOT_STARTED, db_index=True)
    notified_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["assignment", "recipient_type", "recipient_id"]
        indexes = [
            models.Index(fields=["assignment", "status"]),
            models.Index(fields=["recipient_type", "recipient_id"]),
            models.Index(fields=["organization", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["assignment", "recipient_type", "recipient_id"], name="forms_unique_assignment_recipient"),
        ]

    def __str__(self):
        return f"{self.assignment.title} recipient {self.recipient_type}:{self.recipient_id}"


class FormResponse(UUIDModel, TimestampedModel):
    assignment = models.ForeignKey(FormAssignment, on_delete=models.CASCADE, related_name="responses")
    template = models.ForeignKey(FormTemplate, on_delete=models.PROTECT, related_name="responses")
    template_version = models.ForeignKey(FormTemplateVersion, on_delete=models.PROTECT, null=True, related_name="responses")
    recipient = models.ForeignKey(FormRecipient, on_delete=models.SET_NULL, null=True, blank=True, related_name="responses")
    respondent_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="form_responses")
    respondent_organization = models.ForeignKey(Organization, on_delete=models.PROTECT, null=True, blank=True, related_name="form_responses")
    context_type = models.CharField(max_length=50, blank=True)
    context_id = models.CharField(max_length=100, blank=True)
    response_json = models.JSONField(default=dict)
    score = models.FloatField(null=True, blank=True)
    risk_rating = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=ResponseStatus.choices, default=ResponseStatus.NOT_STARTED, db_index=True)
    sync_status = models.CharField(max_length=20, choices=FormSyncStatus.choices, default=FormSyncStatus.ONLINE, db_index=True)
    device_id = models.CharField(max_length=128, blank=True)
    offline_created_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    last_saved_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="responses_reviewed")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    returned_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["sync_status"]),
            models.Index(fields=["assignment"]),
            models.Index(fields=["respondent_user"]),
            models.Index(fields=["context_type", "context_id"]),
        ]

    def __str__(self):
        return f"Response by {self.respondent_user} for {self.template.title}"


class FormResponseAttachment(UUIDModel, TimestampedModel):
    response = models.ForeignKey(FormResponse, on_delete=models.CASCADE, related_name="attachments")
    question_key = models.CharField(max_length=120)
    repeat_group_key = models.CharField(max_length=120, blank=True)
    repeat_item_id = models.CharField(max_length=120, blank=True)
    file = models.FileField(upload_to="form_response_attachments/", null=True, blank=True)
    file_url = models.URLField(blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveBigIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=120, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="form_response_attachments")
    captured_at = models.DateTimeField(null=True, blank=True)
    gps_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    metadata_json = models.JSONField(default=dict, blank=True)
    sync_status = models.CharField(max_length=20, choices=FormSyncStatus.choices, default=FormSyncStatus.ONLINE, db_index=True)

    class Meta:
        ordering = ["response", "question_key", "created_at"]
        indexes = [
            models.Index(fields=["response", "question_key"]),
            models.Index(fields=["sync_status"]),
        ]

    def __str__(self):
        return self.file_name or self.file_url or f"Attachment for {self.question_key}"


class FormResponseActivityLog(UUIDModel, TimestampedModel):
    response = models.ForeignKey(FormResponse, on_delete=models.CASCADE, related_name="activity_logs")
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="form_response_activity")
    action = models.CharField(max_length=64, db_index=True)
    details_json = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_id = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["response", "action"]),
            models.Index(fields=["actor", "created_at"]),
        ]

    def __str__(self):
        return f"{self.action} on {self.response_id}"


class OfflineSyncQueue(UUIDModel, TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="form_offline_sync_jobs")
    assignment = models.ForeignKey(FormAssignment, on_delete=models.CASCADE, null=True, blank=True, related_name="offline_sync_jobs")
    response = models.ForeignKey(FormResponse, on_delete=models.SET_NULL, null=True, blank=True, related_name="offline_sync_jobs")
    local_response_id = models.CharField(max_length=128, db_index=True)
    operation_type = models.CharField(max_length=50)
    payload_json = models.JSONField(default=dict, blank=True)
    media_payload_ref = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=FormSyncStatus.choices, default=FormSyncStatus.SYNC_PENDING, db_index=True)
    attempt_count = models.PositiveIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["assignment", "status"]),
            models.Index(fields=["local_response_id"]),
        ]

    def mark_attempt(self, error_message: str = ""):
        self.attempt_count += 1
        self.last_attempt_at = timezone.now()
        if error_message:
            self.status = FormSyncStatus.SYNC_FAILED
            self.error_message = error_message
        self.save(update_fields=["attempt_count", "last_attempt_at", "status", "error_message", "updated_at"])
