from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.models import UserInvite, UserRole
from apps.accounts.serializers import UserInviteSerializer, UserSerializer
from apps.audit.models import AuditLog
from apps.certificates.models import Certificate, CertificateRequest, CertificateStatus
from apps.employers.models import Employer
from apps.facilities.models import MedicalFacility
from apps.food_handlers.models import FoodHandlerProfile
from apps.illness.models import IllnessReport
from apps.inspections.models import Inspection
from apps.inspections.serializers import InspectionResponseSerializer, InspectionSerializer
from apps.ministries.models import FederalStateQuery, MinistryStaffProfile, StateReport
from apps.organizations.models import OrganizationUnit
from apps.reports.models import GeneratedReport, ReportType
from apps.organizations.serializers import OrganizationUnitSerializer
from apps.policy.serializers import NationalPolicyConfigSerializer, StatePolicyConfigSerializer
from apps.reports.serializers import DashboardQuerySerializer


User = get_user_model()


class MinistryStaffProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)

    class Meta:
        model = MinistryStaffProfile
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "ministry_type",
            "sub_role",
            "state",
            "state_name",
            "lga",
            "lga_name",
            "unit",
            "unit_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StateMinistryUserSerializer(UserSerializer):
    ministry_profile = MinistryStaffProfileSerializer(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("ministry_profile",)


class StateMinistryInviteCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=[UserRole.STATE_ADMIN, UserRole.INSPECTOR])
    ministry_staff_role = serializers.CharField(required=False, allow_blank=True)
    unit = serializers.PrimaryKeyRelatedField(queryset=OrganizationUnit.objects.all(), required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    message = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False)


class StateMinistryInviteSerializer(UserInviteSerializer):
    pass


class StateCertificateValidationSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="assessment.food_handler.full_name", read_only=True)
    food_handler_category = serializers.CharField(source="assessment.food_handler.food_handler_category", read_only=True)
    employer_name = serializers.CharField(source="assessment.employer.business_name", read_only=True)
    facility_name = serializers.CharField(source="assessment.facility.facility_name", read_only=True)
    facility_id = serializers.UUIDField(source="assessment.facility.id", read_only=True)
    issuing_state_name = serializers.CharField(source="assessment.facility.state.name", read_only=True)
    final_decision = serializers.CharField(source="assessment.final_decision", read_only=True)
    payment_status = serializers.CharField(source="assessment.payment_transaction.status", read_only=True)
    declaration_status = serializers.CharField(source="assessment.declaration_status", read_only=True)
    physical_exam_status = serializers.CharField(source="assessment.physical_exam_status", read_only=True)
    lab_status = serializers.CharField(source="assessment.lab_status", read_only=True)
    vaccination_status = serializers.CharField(source="assessment.vaccination_status", read_only=True)
    certificate_id = serializers.UUIDField(source="assessment.certificate.id", read_only=True)
    certificate_number = serializers.CharField(source="assessment.certificate.certificate_number", read_only=True)
    requested_by_name = serializers.CharField(source="requested_by.get_full_name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)
    facility_responded_by_name = serializers.CharField(source="facility_responded_by.get_full_name", read_only=True)
    assessment_evidence_summary = serializers.SerializerMethodField()

    class Meta:
        model = CertificateRequest
        fields = (
            "id",
            "assessment",
            "food_handler_name",
            "food_handler_category",
            "employer_name",
            "facility_id",
            "facility_name",
            "issuing_state_name",
            "final_decision",
            "payment_status",
            "declaration_status",
            "physical_exam_status",
            "lab_status",
            "vaccination_status",
            "certificate_id",
            "certificate_number",
            "requested_by",
            "requested_by_name",
            "reviewed_by",
            "reviewed_by_name",
            "status",
            "request_notes",
            "review_notes",
            "reviewed_at",
            "facility_response",
            "facility_responded_by",
            "facility_responded_by_name",
            "facility_responded_at",
            "assessment_evidence_summary",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_assessment_evidence_summary(self, obj):
        assessment = obj.assessment
        return {
            "fit_signed": assessment.final_decision == "fit" and bool(assessment.signed_at),
            "payment_status": assessment.payment_transaction.status if assessment.payment_transaction else "missing",
            "declaration_status": assessment.declaration_status,
            "physical_exam_status": assessment.physical_exam_status,
            "lab_status": assessment.lab_status,
            "vaccination_status": assessment.vaccination_status,
            "medical_report_generated": GeneratedReport.objects.filter(
                filters__assessment_id=str(assessment.id),
                report_type__in=[ReportType.MEDICAL_EXAMINATION, ReportType.ASSESSMENT_COMPLETION],
            ).exists(),
        }


class StateCertificateValidationActionSerializer(serializers.Serializer):
    review_notes = serializers.CharField(required=False, allow_blank=True)


class StateCertificateRegistrySerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    food_handler_category = serializers.CharField(source="food_handler.food_handler_category", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    issuing_state_name = serializers.CharField(source="issuing_state.name", read_only=True)
    effective_status = serializers.CharField(read_only=True)
    suspended_by_name = serializers.CharField(source="suspended_by.get_full_name", read_only=True)
    revoked_by_name = serializers.CharField(source="revoked_by.get_full_name", read_only=True)

    class Meta:
        model = Certificate
        fields = (
            "id",
            "certificate_number",
            "food_handler",
            "food_handler_name",
            "food_handler_category",
            "employer",
            "employer_name",
            "facility",
            "facility_name",
            "issuing_state",
            "issuing_state_name",
            "issue_date",
            "expiry_date",
            "status",
            "effective_status",
            "verification_url",
            "suspended_by",
            "suspended_by_name",
            "suspended_at",
            "suspension_reason",
            "replaced_by",
            "replacement_reason",
            "revoked_by",
            "revoked_by_name",
            "revoked_at",
            "revocation_reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class StateCertificateLifecycleActionSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, allow_blank=False)


class StateEmployerMonitoringSerializer(serializers.ModelSerializer):
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    food_handler_count = serializers.SerializerMethodField()
    active_certificate_count = serializers.SerializerMethodField()
    active_illness_exclusion_count = serializers.SerializerMethodField()

    class Meta:
        model = Employer
        fields = (
            "id",
            "business_name",
            "establishment_category",
            "business_registration_number",
            "lga",
            "lga_name",
            "compliance_status",
            "subscription_status",
            "is_active",
            "food_handler_count",
            "active_certificate_count",
            "active_illness_exclusion_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_food_handler_count(self, obj):
        return obj.food_handlers.count()

    def get_active_certificate_count(self, obj):
        return Certificate.objects.filter(
            employer=obj,
            status=CertificateStatus.ACTIVE,
        ).count()

    def get_active_illness_exclusion_count(self, obj):
        return obj.illness_reports.exclude(clearance_status__in=["cleared", "rejected"]).count()


class StateFoodHandlerMonitoringSerializer(serializers.ModelSerializer):
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    branch_name = serializers.CharField(source="business_branch.name", read_only=True)
    certificate_status = serializers.SerializerMethodField()
    certificate_number = serializers.SerializerMethodField()
    certificate_expiry_date = serializers.SerializerMethodField()
    active_illness_status = serializers.SerializerMethodField()

    class Meta:
        model = FoodHandlerProfile
        fields = (
            "id",
            "full_name",
            "system_identifier",
            "state",
            "lga",
            "lga_name",
            "employer",
            "employer_name",
            "business_branch",
            "branch_name",
            "food_handler_category",
            "current_status",
            "certificate_status",
            "certificate_number",
            "certificate_expiry_date",
            "active_illness_status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def latest_certificate(self, obj):
        return obj.certificates.order_by("-issue_date", "-created_at").first()

    def get_certificate_status(self, obj):
        certificate = self.latest_certificate(obj)
        return certificate.effective_status if certificate else "not_issued"

    def get_certificate_number(self, obj):
        certificate = self.latest_certificate(obj)
        return certificate.certificate_number if certificate else ""

    def get_certificate_expiry_date(self, obj):
        certificate = self.latest_certificate(obj)
        return certificate.expiry_date if certificate else None

    def get_active_illness_status(self, obj):
        report = obj.illness_reports.exclude(clearance_status__in=["cleared", "rejected"]).order_by("-created_at").first()
        return report.clearance_status if report else ""


class StateIllnessMonitoringSerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    food_handler_category = serializers.CharField(source="food_handler.food_handler_category", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    lga_name = serializers.CharField(source="food_handler.lga.name", read_only=True)

    class Meta:
        model = IllnessReport
        fields = (
            "id",
            "food_handler",
            "food_handler_name",
            "food_handler_category",
            "employer",
            "employer_name",
            "lga_name",
            "suspected_condition",
            "exclusion_start_date",
            "earliest_return_date",
            "clearance_required",
            "clearance_status",
            "cleared_at",
            "return_to_work_certificate_number",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class StateInspectionAssignmentSerializer(serializers.Serializer):
    inspector = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    employer = serializers.PrimaryKeyRelatedField(queryset=Employer.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=OrganizationUnit.objects.all(), required=False, allow_null=True)
    inspection_date = serializers.DateTimeField(required=False)
    checklist_responses = serializers.JSONField(required=False)
    enforcement_action = serializers.CharField(required=False, allow_blank=True)
    findings = serializers.CharField(required=False, allow_blank=True)


class StateInspectionReviewSerializer(serializers.Serializer):
    checklist_responses = serializers.JSONField(required=False)
    enforcement_action = serializers.CharField(required=False, allow_blank=True)
    findings = serializers.CharField(required=False, allow_blank=True)
    evidence_files = serializers.JSONField(required=False)


class StateInspectionCloseSerializer(serializers.Serializer):
    closure_notes = serializers.CharField(required=False, allow_blank=True)


class StateInspectionSerializer(InspectionSerializer):
    state_name = serializers.CharField(source="employer.state.name", read_only=True)
    lga_name = serializers.CharField(source="employer.lga.name", read_only=True)
    responses = InspectionResponseSerializer(source="employer_responses", many=True, read_only=True)
    audit_history = serializers.SerializerMethodField()

    class Meta(InspectionSerializer.Meta):
        model = Inspection
        fields = InspectionSerializer.Meta.fields + (
            "state_name",
            "lga_name",
            "responses",
            "audit_history",
        )
        read_only_fields = fields

    def get_audit_history(self, obj):
        logs = AuditLog.objects.filter(target_type="Inspection", target_id=str(obj.id)).select_related("actor").order_by("-created_at")[:20]
        return [
            {
                "id": str(log.id),
                "action": log.action,
                "actor_name": log.actor.get_full_name() if log.actor else "",
                "metadata": log.metadata,
                "created_at": log.created_at,
            }
            for log in logs
        ]


class StateReportSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    generated_by_name = serializers.CharField(source="generated_by.get_full_name", read_only=True)
    submitted_by_name = serializers.CharField(source="submitted_by.get_full_name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)

    class Meta:
        model = StateReport
        fields = (
            "id",
            "state",
            "state_name",
            "report_type",
            "reporting_period_start",
            "reporting_period_end",
            "status",
            "generated_by",
            "generated_by_name",
            "submitted_by",
            "submitted_by_name",
            "submitted_at",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "file_url",
            "data_snapshot",
            "review_comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class StateReportGenerateSerializer(serializers.Serializer):
    report_type = serializers.CharField(default="state_monthly")
    reporting_period_start = serializers.DateField()
    reporting_period_end = serializers.DateField()

    def validate(self, attrs):
        if attrs["reporting_period_end"] < attrs["reporting_period_start"]:
            raise serializers.ValidationError("Reporting period end must be on or after the start date.")
        return attrs


class FederalCertificateRegistrySerializer(serializers.ModelSerializer):
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    employer_name = serializers.CharField(source="employer.business_name", read_only=True)
    facility_name = serializers.CharField(source="facility.facility_name", read_only=True)
    issuing_state_name = serializers.CharField(source="issuing_state.name", read_only=True)
    effective_status = serializers.CharField(read_only=True)
    suspicious_report_count = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = (
            "id",
            "certificate_number",
            "food_handler_name",
            "employer_name",
            "facility_name",
            "issuing_state",
            "issuing_state_name",
            "issue_date",
            "expiry_date",
            "status",
            "effective_status",
            "suspicious_report_count",
            "verification_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_suspicious_report_count(self, obj):
        if hasattr(obj, "suspicious_report_count"):
            return obj.suspicious_report_count
        return obj.suspicious_reports.count()


class FederalFacilityRegistrySerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    can_conduct_assessments = serializers.BooleanField(read_only=True)

    class Meta:
        model = MedicalFacility
        fields = (
            "id",
            "facility_name",
            "facility_type",
            "ownership_type",
            "license_number",
            "registration_number",
            "state",
            "state_name",
            "lga",
            "lga_name",
            "accreditation_status",
            "accreditation_start_date",
            "accreditation_expiry_date",
            "can_conduct_assessments",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class FederalEmployerRegistrySerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    food_handler_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employer
        fields = (
            "id",
            "business_name",
            "establishment_category",
            "business_registration_number",
            "state",
            "state_name",
            "lga",
            "lga_name",
            "compliance_status",
            "subscription_status",
            "is_active",
            "food_handler_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class FederalFoodHandlerSummarySerializer(serializers.Serializer):
    totals = serializers.DictField()
    by_state = serializers.ListField()
    by_category = serializers.ListField()
    by_status = serializers.ListField()


class FederalStateQuerySerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    raised_by_name = serializers.CharField(source="raised_by.get_full_name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)
    responded_by_name = serializers.CharField(source="responded_by.get_full_name", read_only=True)

    class Meta:
        model = FederalStateQuery
        fields = (
            "id",
            "state",
            "state_name",
            "subject",
            "description",
            "category",
            "priority",
            "status",
            "raised_by",
            "raised_by_name",
            "assigned_to",
            "assigned_to_name",
            "response",
            "responded_by",
            "responded_by_name",
            "responded_at",
            "closed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "raised_by", "raised_by_name", "responded_by", "responded_by_name", "responded_at", "closed_at", "created_at", "updated_at")


class FederalStateQueryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FederalStateQuery
        fields = ("state", "subject", "description", "category", "priority", "assigned_to")


class FederalStateQueryResponseSerializer(serializers.Serializer):
    response = serializers.CharField(required=True, allow_blank=False)


__all__ = [
    "DashboardQuerySerializer",
    "MinistryStaffProfileSerializer",
    "OrganizationUnitSerializer",
    "StateMinistryInviteCreateSerializer",
    "StateMinistryInviteSerializer",
    "StateMinistryUserSerializer",
    "StateCertificateValidationActionSerializer",
    "StateCertificateValidationSerializer",
    "StateCertificateLifecycleActionSerializer",
    "StateCertificateRegistrySerializer",
    "StateEmployerMonitoringSerializer",
    "StateFoodHandlerMonitoringSerializer",
    "StateIllnessMonitoringSerializer",
    "StateInspectionAssignmentSerializer",
    "StateInspectionCloseSerializer",
    "StateInspectionReviewSerializer",
    "StateInspectionSerializer",
    "StateReportGenerateSerializer",
    "StateReportSerializer",
    "FederalCertificateRegistrySerializer",
    "FederalEmployerRegistrySerializer",
    "FederalFacilityRegistrySerializer",
    "FederalFoodHandlerSummarySerializer",
    "FederalStateQueryCreateSerializer",
    "FederalStateQueryResponseSerializer",
    "FederalStateQuerySerializer",
    "NationalPolicyConfigSerializer",
    "StatePolicyConfigSerializer",
]
