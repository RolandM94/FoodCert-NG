from rest_framework import serializers

from apps.certificates.models import Certificate
from apps.employers.models import Employer
from apps.inspections.models import (
    ChecklistCategory,
    ChecklistResponseChoice,
    ChecklistSeverity,
    CorrectiveActionResponse,
    CorrectiveActionStatus,
    EnforcementCase,
    EnforcementNotice,
    EvidenceType,
    FindingStatus,
    FindingType,
    Inspection,
    InspectionCertificateScan,
    InspectionChecklistItem,
    InspectionChecklistResponse,
    InspectionEvidence,
    InspectionFinding,
    InspectionPriority,
    InspectionResponse,
    InspectionResponseType,
    InspectionStatus,
    InspectionType,
    NoticeStatus,
    NoticeType,
)


class InspectionSerializer(serializers.ModelSerializer):
    inspector_name = serializers.CharField(source="inspector.get_full_name", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    assigned_by_name = serializers.CharField(source="assigned_by.get_full_name", read_only=True)
    supervising_officer_name = serializers.CharField(source="supervising_officer.get_full_name", read_only=True)

    class Meta:
        model = Inspection
        fields = (
            "id",
            "reference",
            "inspection_type",
            "priority",
            "inspector",
            "inspector_name",
            "employer",
            "employer_name",
            "branch",
            "branch_name",
            "assigned_by",
            "assigned_by_name",
            "supervising_officer",
            "supervising_officer_name",
            "parent_inspection",
            "linked_complaint_id",
            "linked_illness_report_id",
            "inspection_date",
            "scheduled_at",
            "started_at",
            "submitted_at",
            "reviewed_at",
            "closed_at",
            "gps_latitude",
            "gps_longitude",
            "reason",
            "checklist_responses",
            "compliance_score",
            "enforcement_action",
            "findings",
            "summary",
            "evidence_files",
            "status",
            "cancellation_reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id", "reference", "inspector", "inspector_name", "assigned_by_name",
            "supervising_officer_name", "compliance_score", "evidence_files",
            "submitted_at", "created_at", "updated_at",
        )


class InspectionResponseSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source="submitted_by.get_full_name", read_only=True)

    class Meta:
        model = InspectionResponse
        fields = (
            "id",
            "inspection",
            "submitted_by",
            "submitted_by_name",
            "response_type",
            "content",
            "evidence_file_url",
            "submitted_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class InspectionResponseCreateSerializer(serializers.Serializer):
    response_type = serializers.ChoiceField(choices=InspectionResponseType.choices)
    content = serializers.CharField(required=False, allow_blank=True)
    evidence_file_url = serializers.URLField(required=False, allow_blank=True)


class CreateInspectionSerializer(serializers.ModelSerializer):
    employer = serializers.PrimaryKeyRelatedField(queryset=Employer.objects.all())

    class Meta:
        model = Inspection
        fields = (
            "employer",
            "branch",
            "inspection_type",
            "priority",
            "inspection_date",
            "scheduled_at",
            "gps_latitude",
            "gps_longitude",
            "reason",
            "checklist_responses",
            "enforcement_action",
            "findings",
            "summary",
            "status",
        )


class InspectionEvidenceSerializer(serializers.Serializer):
    file_url = serializers.URLField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    uploaded_at = serializers.DateTimeField(required=False)


class CertificateScanSerializer(serializers.Serializer):
    certificate_number = serializers.CharField()


class InspectionCertificateScanSerializer(serializers.ModelSerializer):
    certificate_status = serializers.CharField(source="certificate.effective_status", read_only=True)
    food_handler_name = serializers.CharField(source="certificate.food_handler.full_name", read_only=True)
    issuing_state_name = serializers.CharField(source="certificate.issuing_state.name", read_only=True)
    facility_name = serializers.CharField(source="certificate.facility.facility_name", read_only=True)

    class Meta:
        model = InspectionCertificateScan
        fields = (
            "id",
            "inspection",
            "certificate_number",
            "certificate",
            "certificate_status",
            "food_handler_name",
            "issuing_state_name",
            "facility_name",
            "result",
            "scanned_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class InspectorCertificateVerificationSerializer(serializers.ModelSerializer):
    certificate_validity = serializers.CharField(source="effective_status", read_only=True)
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    passport_photo = serializers.ImageField(source="food_handler.passport_photo", read_only=True)
    issuing_state_ministry = serializers.SerializerMethodField()
    approved_medical_facility = serializers.CharField(source="facility.facility_name", read_only=True)
    fitness_status = serializers.CharField(source="assessment.final_decision", read_only=True)
    verification_result = serializers.CharField(read_only=True)

    class Meta:
        model = Certificate
        fields = (
            "id",
            "certificate_number",
            "certificate_validity",
            "verification_result",
            "food_handler_name",
            "passport_photo",
            "issuing_state_ministry",
            "approved_medical_facility",
            "issue_date",
            "expiry_date",
            "fitness_status",
        )

    def get_issuing_state_ministry(self, obj) -> str:
        return f"{obj.issuing_state.name} State Ministry of Health"

    def to_representation(self, instance):
        payload = super().to_representation(instance)
        payload["verification_result"] = self.context.get("verification_result", payload.get("certificate_validity"))
        payload["certificate_validity"] = self.context.get("verification_result", payload.get("certificate_validity"))
        return payload


class InspectorCertificateNumberSerializer(serializers.Serializer):
    certificate_number = serializers.CharField(max_length=96)


class InspectorCertificateSaveSerializer(serializers.Serializer):
    inspection = serializers.PrimaryKeyRelatedField(queryset=Inspection.objects.all())


class InspectorCertificateFlagSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255)
    details = serializers.CharField(required=False, allow_blank=True)


class InspectionChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionChecklistItem
        fields = (
            "id",
            "category",
            "question",
            "severity_if_failed",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class InspectionChecklistResponseSerializer(serializers.ModelSerializer):
    checklist_item_question = serializers.CharField(source="checklist_item.question", read_only=True)
    checklist_item_category = serializers.CharField(source="checklist_item.category", read_only=True)
    checklist_item_severity = serializers.CharField(source="checklist_item.severity_if_failed", read_only=True)

    class Meta:
        model = InspectionChecklistResponse
        fields = (
            "id",
            "inspection",
            "checklist_item",
            "checklist_item_question",
            "checklist_item_category",
            "checklist_item_severity",
            "response",
            "severity",
            "note",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "checklist_item_question", "checklist_item_category", "checklist_item_severity", "created_by", "created_at", "updated_at")


class InspectionFindingSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    certificate_number = serializers.CharField(source="certificate.certificate_number", read_only=True)

    class Meta:
        model = InspectionFinding
        fields = (
            "id",
            "inspection",
            "category",
            "finding_type",
            "severity",
            "description",
            "recommended_action",
            "food_handler",
            "food_handler_name",
            "certificate",
            "certificate_number",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "food_handler_name", "certificate_number", "created_by", "created_at", "updated_at")


class InspectionFindingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionFinding
        fields = (
            "category",
            "finding_type",
            "severity",
            "description",
            "recommended_action",
            "food_handler",
            "certificate",
        )


class InspectionEvidenceSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.get_full_name", read_only=True)

    class Meta:
        model = InspectionEvidence
        fields = (
            "id",
            "inspection",
            "finding",
            "evidence_type",
            "file_url",
            "caption",
            "uploaded_by",
            "uploaded_by_name",
            "latitude",
            "longitude",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "uploaded_by", "uploaded_by_name", "created_at", "updated_at")


class EnforcementNoticeSerializer(serializers.ModelSerializer):
    issued_by_name = serializers.CharField(source="issued_by.get_full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = EnforcementNotice
        fields = (
            "id",
            "notice_reference",
            "inspection",
            "employer",
            "employer_name",
            "branch",
            "branch_name",
            "notice_type",
            "status",
            "description",
            "required_corrective_actions",
            "deadline",
            "issued_by",
            "issued_by_name",
            "approved_by",
            "approved_by_name",
            "issued_at",
            "acknowledged_at",
            "closed_at",
            "closure_note",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "notice_reference", "issued_by_name", "approved_by_name", "employer_name", "branch_name", "issued_at", "acknowledged_at", "created_at", "updated_at")


class EnforcementNoticeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnforcementNotice
        fields = (
            "inspection",
            "employer",
            "branch",
            "notice_type",
            "description",
            "required_corrective_actions",
            "deadline",
        )


class CorrectiveActionResponseSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source="submitted_by.get_full_name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)
    notice_reference = serializers.CharField(source="notice.notice_reference", read_only=True)

    class Meta:
        model = CorrectiveActionResponse
        fields = (
            "id",
            "notice",
            "notice_reference",
            "submitted_by",
            "submitted_by_name",
            "response_note",
            "action_taken",
            "status",
            "reviewed_by",
            "reviewed_by_name",
            "review_note",
            "submitted_at",
            "reviewed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "submitted_by_name", "reviewed_by_name", "notice_reference", "submitted_at", "reviewed_at", "created_at", "updated_at")


class CorrectiveActionResponseCreateSerializer(serializers.Serializer):
    response_note = serializers.CharField()
    action_taken = serializers.CharField()
    evidence_file_url = serializers.URLField(required=False, allow_blank=True)


class EnforcementCaseSerializer(serializers.ModelSerializer):
    opened_by_name = serializers.CharField(source="opened_by.get_full_name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)

    class Meta:
        model = EnforcementCase
        fields = (
            "id",
            "case_reference",
            "state",
            "state_name",
            "employer",
            "employer_name",
            "branch",
            "status",
            "severity",
            "summary",
            "opened_by",
            "opened_by_name",
            "assigned_to",
            "assigned_to_name",
            "escalated_to",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "case_reference", "opened_by_name", "assigned_to_name", "employer_name", "state_name", "created_at", "updated_at")
