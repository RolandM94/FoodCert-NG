import csv
import io

from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from django.core.cache import cache
from django.utils.dateparse import parse_date
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from apps.accounts.permissions import IsActiveUser
from apps.audit.models import AuditAction, AuditLog
from apps.audit.services import log_action

from .models import (
    AcknowledgementStatus,
    Approval,
    ApprovalStatus,
    CertificateTemplate,
    CertificateValidityRule,
    EstablishmentCategory,
    FacilityRequirementRule,
    FoodHandlerCategory,
    IndicatorCalculationStatus,
    IndicatorDisaggregatedValue,
    IndicatorEvidence,
    MEIndicator,
    MEIndicatorDataSource,
    MEIndicatorValue,
    MEIndicatorValueHistory,
    IndicatorAdoption,
    IndicatorLifecycleStatus,
    IndicatorManualEntry,
    IndicatorManualEntryReviewStatus,
    IndicatorScopeType,
    IndicatorTarget,
    IndicatorThreshold,
    MedicalTestPackage,
    MedicalTestPackageComponent,
    MedicalTestRule,
    PhysicalExaminationRule,
    PolicyDocument,
    PolicyVersion,
    PolicyVersionStatus,
    ReportingTemplate,
    ReturnToWorkRule,
    StateAcknowledgement,
    StateConfigurationControl,
    VaccinationRule,
)
from .permissions import (
    FEDERAL_STANDARDS_ROLES,
    CanAcknowledgePolicy,
    CanApprovePolicyVersion,
    CanManageStandards,
    CanViewStandardsAudit,
)
from .serializers import (
    ApprovalActionSerializer,
    ApprovalSerializer,
    CertificateTemplateSerializer,
    CertificateValidityRuleSerializer,
    EstablishmentCategorySerializer,
    FacilityRequirementRuleSerializer,
    FoodHandlerCategorySerializer,
    IndicatorDisaggregationSerializer,
    IndicatorEvidenceSerializer,
    MEIndicatorCalculationLogSerializer,
    MEIndicatorCalculationSerializer,
    MEIndicatorDataSourceSerializer,
    MEIndicatorFormSourceSerializer,
    MEIndicatorIndicatorSourceSerializer,
    MEIndicatorOverrideSerializer,
    MEIndicatorSerializer,
    MEIndicatorValueSerializer,
    IndicatorAdoptionSerializer,
    IndicatorManualEntrySerializer,
    IndicatorTargetSerializer,
    IndicatorThresholdSerializer,
    MedicalTestPackageSerializer,
    MedicalTestPackageComponentSerializer,
    MedicalTestRuleSerializer,
    PhysicalExaminationRuleSerializer,
    PolicyDocumentSerializer,
    PolicyVersionCreateSerializer,
    PolicyVersionDetailSerializer,
    PolicyVersionPublishSerializer,
    PolicyVersionSerializer,
    ReportingTemplateSerializer,
    ReturnToWorkRuleSerializer,
    StateAcknowledgementSerializer,
    StateConfigurationControlSerializer,
    StandardsAuditLogSerializer,
    VaccinationRuleSerializer,
)
from .services import ACTIVE_STANDARDS_CACHE_VERSION_KEY, ActivePolicyRuleError, PolicyVersionService
from .kpi_engine import FoodHandlersKpiCalculationService, KPIEngineError
from .indicator_calculations import (
    IndicatorCalculationError,
    IndicatorCalculationService,
    IndicatorFormSourceAdapter,
    IndicatorIndicatorSourceAdapter,
)


def _build_state_comparison(indicator_rows, approved_values):
    """Build per-state KPI achievement comparison from disaggregated values.

    Extracts state-level dimension values from IndicatorDisaggregatedValue
    and returns a ranking of states by KPI achievement.
    """
    indicator_ids = [i.id for i in indicator_rows]
    disaggregated = IndicatorDisaggregatedValue.objects.filter(
        indicator_id__in=indicator_ids,
    ).select_related("indicator")

    if approved_values is not None:
        approved_value_ids = set(approved_values.values_list("id", flat=True))
        disaggregated = disaggregated.filter(indicator_value_id__in=approved_value_ids)

    state_data = {}
    for item in disaggregated:
        dims = item.dimension_values_json or {}
        state_name = dims.get("state") or dims.get("state_name") or dims.get("state_code")
        if not state_name:
            continue
        state_name = str(state_name)
        state_data.setdefault(state_name, {"kpi_count": 0, "total_value": 0.0, "achievement_sum": 0.0, "achievement_count": 0})

        entry = state_data[state_name]
        entry["kpi_count"] += 1
        val = float(item.value_numeric) if item.value_numeric is not None else 0
        entry["total_value"] += val

        target = item.indicator.target_value
        if target and val > 0:
            entry["achievement_sum"] += (val / float(target)) * 100
            entry["achievement_count"] += 1

    comparison = []
    for state_name, data in state_data.items():
        avg_achievement = round(data["achievement_sum"] / data["achievement_count"], 1) if data["achievement_count"] else None
        comparison.append({
            "state": state_name,
            "kpi_count": data["kpi_count"],
            "total_value": round(data["total_value"], 2),
            "achievement": avg_achievement,
        })
    comparison.sort(key=lambda s: (s["achievement"] is None, -(s["achievement"] or 0)))
    return comparison


class PolicyVersionViewSet(viewsets.ModelViewSet):
    queryset = PolicyVersion.objects.all()
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageStandards]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["status", "version_type"]
    search_fields = ["version_code", "title"]
    ordering_fields = ["created_at", "effective_start_date"]

    def get_serializer_class(self):
        if self.action == "create":
            return PolicyVersionCreateSerializer
        if self.action == "retrieve":
            return PolicyVersionDetailSerializer
        return PolicyVersionSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        qs = PolicyVersion.objects.select_related(
            "created_by", "submitted_by", "approved_by", "published_by",
        ).annotate(
            handler_category_count=Count("food_handler_categories"),
            medical_test_rule_count=Count("medical_test_rules"),
            vaccination_rule_count=Count("vaccination_rules"),
            acknowledgement_count=Count(
                "state_acknowledgements",
                filter=Q(state_acknowledgements__status=AcknowledgementStatus.ACKNOWLEDGED),
            ),
        )
        user = self.request.user
        if user.role in FEDERAL_STANDARDS_ROLES:
            return qs
        if user.role == "state_admin":
            return qs.filter(status__in=[
                PolicyVersionStatus.ACTIVE, PolicyVersionStatus.SCHEDULED,
            ])
        if user.role == "facility_admin":
            return qs.filter(status=PolicyVersionStatus.ACTIVE)
        return qs.none()

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        log_action(
            action=AuditAction.CREATE,
            actor=self.request.user,
            target=instance,
            metadata={"event": "policy_version_created"},
            request=self.request,
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.status != PolicyVersionStatus.DRAFT and instance.status != PolicyVersionStatus.RETURNED:
            return Response(
                {"detail": "Only draft or returned versions can be edited."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        old = PolicyVersionSerializer(instance).data
        instance = serializer.save()
        log_action(
            action=AuditAction.UPDATE,
            actor=self.request.user,
            target=instance,
            old_value=old,
            new_value=PolicyVersionSerializer(instance).data,
            metadata={"event": "policy_version_updated"},
            request=self.request,
        )

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        policy_version = self.get_object()
        try:
            PolicyVersionService.submit_for_review(
                policy_version, request.user, request=request,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PolicyVersionSerializer(policy_version).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsActiveUser, CanApprovePolicyVersion])
    def approve(self, request, pk=None):
        policy_version = self.get_object()
        ser = ApprovalActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            PolicyVersionService.approve(
                policy_version, request.user,
                comment=ser.validated_data.get("comment", ""),
                request=request,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PolicyVersionSerializer(policy_version).data)

    @action(detail=True, methods=["post"], url_path="return", permission_classes=[IsAuthenticated, IsActiveUser, CanApprovePolicyVersion])
    def return_version(self, request, pk=None):
        policy_version = self.get_object()
        ser = ApprovalActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            PolicyVersionService.return_for_correction(
                policy_version, request.user,
                comment=ser.validated_data.get("comment", ""),
                request=request,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PolicyVersionSerializer(policy_version).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsActiveUser, CanApprovePolicyVersion])
    def publish(self, request, pk=None):
        policy_version = self.get_object()
        ser = PolicyVersionPublishSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            PolicyVersionService.publish(
                policy_version, request.user,
                effective_date=ser.validated_data.get("effective_date"),
                comment=ser.validated_data.get("comment", ""),
                request=request,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PolicyVersionSerializer(policy_version).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsActiveUser, CanApprovePolicyVersion])
    def retire(self, request, pk=None):
        policy_version = self.get_object()
        try:
            PolicyVersionService.retire(
                policy_version, request.user, request=request,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PolicyVersionSerializer(policy_version).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsActiveUser, CanApprovePolicyVersion])
    def reactivate(self, request, pk=None):
        policy_version = self.get_object()
        try:
            PolicyVersionService.reactivate(
                policy_version, request.user, request=request,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PolicyVersionSerializer(policy_version).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsActiveUser, CanApprovePolicyVersion])
    def archive(self, request, pk=None):
        policy_version = self.get_object()
        try:
            PolicyVersionService.archive(
                policy_version, request.user, request=request,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PolicyVersionSerializer(policy_version).data)

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None):
        source = self.get_object()
        version_code = request.data.get("version_code")
        title = request.data.get("title")
        if not version_code or not title:
            return Response(
                {"detail": "version_code and title are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            new_version = PolicyVersionService.clone(
                source, request.user, version_code, title, request=request,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            PolicyVersionSerializer(new_version).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="compare/(?P<other_id>[^/.]+)")
    def compare(self, request, pk=None, other_id=None):
        version_a = self.get_object()
        try:
            version_b = PolicyVersion.objects.get(pk=other_id)
        except PolicyVersion.DoesNotExist:
            return Response(
                {"detail": "Comparison version not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({
            "version_a": PolicyVersionSerializer(version_a).data,
            "version_b": PolicyVersionSerializer(version_b).data,
        })


class StandardsConfigViewSetMixin:
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageStandards]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        qs = self.queryset.select_related("policy_version", "created_by")
        if user.role in FEDERAL_STANDARDS_ROLES:
            return qs
        if user.role in ("state_admin", "facility_admin"):
            return qs.filter(
                policy_version__status=PolicyVersionStatus.ACTIVE,
            )
        return qs.none()

    def perform_create(self, serializer):
        pv = serializer.validated_data.get("policy_version")
        if pv and pv.status not in (PolicyVersionStatus.DRAFT, PolicyVersionStatus.RETURNED):
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Rules can only be added to draft or returned policy versions.")
        instance = serializer.save(created_by=self.request.user)
        log_action(
            action=AuditAction.CREATE,
            actor=self.request.user,
            target=instance,
            metadata={"event": f"{instance.__class__.__name__.lower()}_created"},
            request=self.request,
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        if hasattr(instance, "status") and instance.status not in ("draft", "returned", "inactive"):
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Only draft or returned rules can be edited.")
        old = self.get_serializer(instance).data
        instance = serializer.save()
        log_action(
            action=AuditAction.UPDATE,
            actor=self.request.user,
            target=instance,
            old_value=old,
            new_value=self.get_serializer(instance).data,
            metadata={"event": f"{instance.__class__.__name__.lower()}_updated"},
            request=self.request,
        )

    def perform_destroy(self, instance):
        if hasattr(instance, "status") and instance.status != "draft":
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Only draft records can be deleted.")
        log_action(
            action=AuditAction.DELETE,
            actor=self.request.user,
            target=instance,
            metadata={"event": f"{instance.__class__.__name__.lower()}_deleted"},
            request=self.request,
        )
        instance.delete()

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        instance = self.get_object()
        if not hasattr(instance, "status") or instance.status != "draft":
            return Response(
                {"detail": "Only draft rules can be submitted for review."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.status = "active"
        instance.save()
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=instance,
            old_value={"status": "draft"},
            new_value={"status": "active"},
            metadata={"event": f"{instance.__class__.__name__.lower()}_activated"},
            request=request,
        )
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=["post"], url_path="retire")
    def retire_rule(self, request, pk=None):
        instance = self.get_object()
        if not hasattr(instance, "status") or instance.status != "active":
            return Response(
                {"detail": "Only active rules can be retired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        old_status = instance.status
        instance.status = "retired"
        instance.save()
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=instance,
            old_value={"status": old_status},
            new_value={"status": "retired"},
            metadata={"event": f"{instance.__class__.__name__.lower()}_retired"},
            request=request,
        )
        return Response(self.get_serializer(instance).data)


class FoodHandlerCategoryViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = FoodHandlerCategory.objects.all()
    serializer_class = FoodHandlerCategorySerializer
    filterset_fields = ["policy_version", "status", "risk_level"]
    search_fields = ["name", "code"]


class EstablishmentCategoryViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = EstablishmentCategory.objects.all()
    serializer_class = EstablishmentCategorySerializer
    filterset_fields = ["policy_version", "status", "risk_level"]
    search_fields = ["name", "code"]


class MedicalTestRuleViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = MedicalTestRule.objects.all()
    serializer_class = MedicalTestRuleSerializer

    @action(detail=True, methods=["post"], url_path="test")
    def test_rule(self, request, pk=None):
        rule = self.get_object()
        if "value" not in request.data:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"value": "A sample 'value' is required to test this rule."})
        return Response(rule.evaluate(request.data.get("value")))
    filterset_fields = ["policy_version", "status", "rule_type", "test_type"]
    search_fields = ["name", "code"]


class PhysicalExaminationRuleViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = PhysicalExaminationRule.objects.all()
    serializer_class = PhysicalExaminationRuleSerializer
    filterset_fields = ["policy_version", "status", "severity"]
    search_fields = ["indicator_name", "code"]


class VaccinationRuleViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = VaccinationRule.objects.all()
    serializer_class = VaccinationRuleSerializer
    filterset_fields = ["policy_version", "status", "required"]
    search_fields = ["vaccine_name", "vaccine_code"]


class CertificateTemplateViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = CertificateTemplate.objects.all()
    serializer_class = CertificateTemplateSerializer
    filterset_fields = ["policy_version", "status"]
    search_fields = ["template_name"]


class CertificateValidityRuleViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = CertificateValidityRule.objects.all()
    serializer_class = CertificateValidityRuleSerializer
    filterset_fields = ["policy_version", "status"]


class ReturnToWorkRuleViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = ReturnToWorkRule.objects.all()
    serializer_class = ReturnToWorkRuleSerializer
    filterset_fields = ["policy_version", "status"]
    search_fields = ["condition_name", "condition_code"]


class FacilityRequirementRuleViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = FacilityRequirementRule.objects.all()
    serializer_class = FacilityRequirementRuleSerializer
    filterset_fields = ["policy_version", "status", "category", "mandatory"]
    search_fields = ["requirement_name", "requirement_code"]


class MedicalTestPackageViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = MedicalTestPackage.objects.prefetch_related("components").all()
    serializer_class = MedicalTestPackageSerializer
    filterset_fields = ["policy_version", "status"]
    search_fields = ["name", "code"]


class IndicatorTargetViewSet(viewsets.ModelViewSet):
    queryset = IndicatorTarget.objects.select_related("indicator", "set_by").all()
    serializer_class = IndicatorTargetSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageStandards]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["indicator", "scope_type", "is_active"]

    def perform_create(self, serializer):
        instance = serializer.save(set_by=self.request.user)
        log_action(action=AuditAction.CREATE, actor=self.request.user, target=instance,
                   metadata={"event": "indicator_target_created", "scope": instance.scope_type}, request=self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(action=AuditAction.UPDATE, actor=self.request.user, target=instance,
                   metadata={"event": "indicator_target_updated"}, request=self.request)


class IndicatorThresholdViewSet(viewsets.ModelViewSet):
    queryset = IndicatorThreshold.objects.select_related("indicator").all()
    serializer_class = IndicatorThresholdSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageStandards]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["indicator", "scope_type", "severity"]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(action=AuditAction.CREATE, actor=self.request.user, target=instance,
                   metadata={"event": "indicator_threshold_created"}, request=self.request)


class IndicatorAdoptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IndicatorAdoption.objects.select_related("federal_indicator", "state", "adopted_by", "cloned_indicator").all()
    serializer_class = IndicatorAdoptionSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageStandards]
    filterset_fields = ["federal_indicator", "state", "adoption_status"]


class IndicatorManualEntryViewSet(viewsets.ModelViewSet):
    queryset = IndicatorManualEntry.objects.select_related("indicator", "submitted_by", "reviewed_by").all()
    serializer_class = IndicatorManualEntrySerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageStandards]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["indicator", "review_status", "scope_type"]

    def perform_create(self, serializer):
        instance = serializer.save(submitted_by=self.request.user)
        log_action(action=AuditAction.CREATE, actor=self.request.user, target=instance,
                   metadata={"event": "indicator_manual_entry_created"}, request=self.request)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        entry = self.get_object()
        if entry.review_status not in (IndicatorManualEntryReviewStatus.DRAFT, IndicatorManualEntryReviewStatus.REJECTED):
            return Response({"detail": "Only draft or rejected entries can be submitted."}, status=status.HTTP_400_BAD_REQUEST)
        entry.review_status = IndicatorManualEntryReviewStatus.SUBMITTED
        entry.submitted_by = request.user
        entry.save(update_fields=["review_status", "submitted_by", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=entry, metadata={"event": "indicator_manual_entry_submitted"})
        return Response(self.get_serializer(entry).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        entry = self.get_object()
        if entry.review_status != IndicatorManualEntryReviewStatus.SUBMITTED:
            return Response({"detail": "Only submitted entries can be approved."}, status=status.HTTP_400_BAD_REQUEST)
        entry.review_status = IndicatorManualEntryReviewStatus.APPROVED
        entry.reviewed_by = request.user
        entry.review_comment = request.data.get("comment", "")
        entry.save(update_fields=["review_status", "reviewed_by", "review_comment", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=entry, metadata={"event": "indicator_manual_entry_approved"})
        return Response(self.get_serializer(entry).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        entry = self.get_object()
        comment = request.data.get("comment", "").strip()
        if not comment:
            return Response({"detail": "A rejection comment is required."}, status=status.HTTP_400_BAD_REQUEST)
        entry.review_status = IndicatorManualEntryReviewStatus.REJECTED
        entry.reviewed_by = request.user
        entry.review_comment = comment
        entry.save(update_fields=["review_status", "reviewed_by", "review_comment", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=entry, metadata={"event": "indicator_manual_entry_rejected"})
        return Response(self.get_serializer(entry).data)


class MedicalTestPackageComponentViewSet(viewsets.ModelViewSet):
    queryset = MedicalTestPackageComponent.objects.select_related("package", "package__policy_version").all()
    serializer_class = MedicalTestPackageComponentSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageStandards]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["package", "component_type", "mandatory"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        qs = self.queryset
        if user.role in FEDERAL_STANDARDS_ROLES:
            return qs
        if user.role in ("state_admin", "facility_admin"):
            return qs.filter(package__policy_version__status=PolicyVersionStatus.ACTIVE)
        return qs.none()

    def _assert_editable(self, package):
        from rest_framework.exceptions import ValidationError

        if package.policy_version.status not in (PolicyVersionStatus.DRAFT, PolicyVersionStatus.RETURNED):
            raise ValidationError("Package components can only be changed on draft or returned policy versions.")

    def perform_create(self, serializer):
        self._assert_editable(serializer.validated_data["package"])
        instance = serializer.save()
        log_action(action=AuditAction.CREATE, actor=self.request.user, target=instance, metadata={"event": "medicaltestpackagecomponent_created"}, request=self.request)

    def perform_update(self, serializer):
        self._assert_editable(serializer.instance.package)
        instance = serializer.save()
        log_action(action=AuditAction.UPDATE, actor=self.request.user, target=instance, metadata={"event": "medicaltestpackagecomponent_updated"}, request=self.request)

    def perform_destroy(self, instance):
        self._assert_editable(instance.package)
        log_action(action=AuditAction.DELETE, actor=self.request.user, target=instance, metadata={"event": "medicaltestpackagecomponent_deleted"}, request=self.request)
        instance.delete()


class ReportingTemplateViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = ReportingTemplate.objects.all()
    serializer_class = ReportingTemplateSerializer
    filterset_fields = ["policy_version", "status", "reporting_frequency"]
    search_fields = ["template_name", "template_code"]


INDICATOR_IMPORT_COLUMNS = [
    "indicator_code",
    "period_start",
    "period_end",
    "progress_value",
    "cumulative_value",
    "qualitative_value",
    "rating_category",
    "notes",
    "evidence_reference",
]


def import_upload_text(request):
    uploaded = request.FILES.get("file")
    if uploaded:
        return uploaded.read().decode("utf-8-sig")
    return request.data.get("csv_text", "")


def clean_import_value(value):
    value = "" if value is None else str(value).strip()
    return value or None


def preview_indicator_import(indicator, csv_text):
    rows = []
    errors = []
    if not csv_text.strip():
        return rows, [{"row": 0, "errors": ["Upload a CSV file or paste CSV text."]}]
    reader = csv.DictReader(io.StringIO(csv_text))
    missing = [column for column in INDICATOR_IMPORT_COLUMNS if column not in (reader.fieldnames or [])]
    if missing:
        return rows, [{"row": 0, "errors": [f"Missing required column: {missing[0]}"]}]

    for index, raw in enumerate(reader, start=2):
        row_errors = []
        indicator_code = (raw.get("indicator_code") or "").strip()
        if indicator_code and indicator_code != indicator.indicator_code:
            row_errors.append("Indicator code does not match this indicator.")
        payload = {
            "indicator": str(indicator.id),
            "period_start": clean_import_value(raw.get("period_start")),
            "period_end": clean_import_value(raw.get("period_end")),
            "progress_value_numeric": clean_import_value(raw.get("progress_value")),
            "cumulative_value_numeric": clean_import_value(raw.get("cumulative_value")),
            "qualitative_value_text": raw.get("qualitative_value") or "",
            "qualitative_rating": None,
            "qualitative_category": "",
            "notes": raw.get("notes") or "",
            "value_source": "import",
            "source_reference_id": f"bulk-import:{indicator.indicator_code}:{raw.get('period_start', '').strip()}:{raw.get('period_end', '').strip()}",
            "evidence_json": [{"reference": raw.get("evidence_reference", "").strip()}] if raw.get("evidence_reference", "").strip() else [],
        }
        rating_category = (raw.get("rating_category") or "").strip()
        try:
            config = getattr(indicator, "qualitative_config", None)
        except Exception:
            config = None
        if config and config.input_type in {"category", "rubric"}:
            payload["qualitative_category"] = rating_category
        elif rating_category:
            payload["qualitative_rating"] = rating_category
        serializer = MEIndicatorValueSerializer(data=payload)
        if not serializer.is_valid():
            row_errors.extend([str(error) for error in serializer.errors.values()])
        approved_exists = MEIndicatorValue.objects.filter(
            indicator=indicator,
            period_start=payload["period_start"],
            period_end=payload["period_end"],
            approval_status="approved",
        ).exists() if payload["period_start"] and payload["period_end"] else False
        if approved_exists:
            row_errors.append("Approved value already exists for this period.")
        rows.append({
            "row": index,
            "data": payload,
            "errors": row_errors,
            "valid": not row_errors,
        })
    return rows, errors


def scoped_kpi_filters_for_user(user):
    filters = {}
    if user.role == "state_admin" and user.state_id:
        filters["state_id"] = str(user.state_id)
    elif user.role == "facility_admin" and getattr(user, "organization_id", None):
        facility = getattr(user.organization, "medical_facility", None)
        if facility:
            filters["facility_id"] = str(facility.id)
            if facility.state_id:
                filters.setdefault("state_id", str(facility.state_id))
    return filters


class MEIndicatorViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = MEIndicator.objects.all()
    serializer_class = MEIndicatorSerializer
    filterset_fields = ["policy_version", "status", "data_source", "mandatory", "owner_type", "visibility", "lifecycle_status", "category"]
    search_fields = ["indicator_name", "indicator_code"]

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        from .indicator_pi import IndicatorLifecycleService
        indicator = self.get_object()
        IndicatorLifecycleService.publish(indicator, request.user, request=request)
        return Response(self.get_serializer(indicator).data)

    @action(detail=True, methods=["post"], url_path="set-lifecycle")
    def set_lifecycle(self, request, pk=None):
        from .indicator_pi import IndicatorLifecycleService
        indicator = self.get_object()
        new_status = request.data.get("lifecycle_status")
        valid = {choice for choice, _ in IndicatorLifecycleStatus.choices}
        if new_status not in valid:
            return Response({"detail": f"lifecycle_status must be one of {sorted(valid)}."}, status=status.HTTP_400_BAD_REQUEST)
        IndicatorLifecycleService.set_lifecycle(indicator, request.user, new_status, request=request)
        return Response(self.get_serializer(indicator).data)

    @action(detail=True, methods=["post"], url_path="share-to-states")
    def share_to_states(self, request, pk=None):
        from .indicator_pi import IndicatorAdoptionService
        indicator = self.get_object()
        state_ids = request.data.get("state_ids") or None
        result = IndicatorAdoptionService.share_to_states(indicator, request.user, state_ids=state_ids, request=request)
        return Response(result)

    @action(detail=True, methods=["get"], url_path="state-adoption")
    def state_adoption(self, request, pk=None):
        indicator = self.get_object()
        adoptions = indicator.adoptions.select_related("state", "adopted_by", "cloned_indicator")
        return Response(IndicatorAdoptionSerializer(adoptions, many=True).data)

    @action(detail=True, methods=["post"])
    def adopt(self, request, pk=None):
        from .indicator_pi import IndicatorAdoptionService
        from apps.ministries.permissions import effective_state_id
        indicator = self.get_object()
        state_id = request.data.get("state_id") or effective_state_id(request.user)
        if not state_id:
            return Response({"detail": "state_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        from apps.locations.models import State
        state = get_object_or_404(State, pk=state_id)
        adoption = IndicatorAdoptionService.adopt(indicator, state, request.user, request=request)
        return Response(IndicatorAdoptionSerializer(adoption).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None):
        from .indicator_pi import IndicatorAdoptionService
        from apps.ministries.permissions import effective_state_id
        indicator = self.get_object()
        state_id = request.data.get("state_id") or effective_state_id(request.user)
        if not state_id:
            return Response({"detail": "state_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        from apps.locations.models import State
        state = get_object_or_404(State, pk=state_id)
        clone = IndicatorAdoptionService.clone_for_state(indicator, state, request.user, request=request)
        return Response(self.get_serializer(clone).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="dashboard-summary")
    def dashboard_summary(self, request):
        indicators = self.filter_queryset(self.get_queryset()).prefetch_related("values", "data_source_configs")
        period_start = parse_date(request.query_params.get("period_start") or "")
        period_end = parse_date(request.query_params.get("period_end") or "")
        status_filter = request.query_params.get("status")
        input_mode_filter = request.query_params.get("input_mode")
        source_filter = request.query_params.get("data_source")
        state_id = request.query_params.get("state_id")
        lga_id = request.query_params.get("lga_id")

        if status_filter:
            indicators = indicators.filter(status=status_filter)
        if input_mode_filter:
            indicators = indicators.filter(input_mode=input_mode_filter)
        if source_filter:
            indicators = indicators.filter(Q(data_source=source_filter) | Q(data_source_configs__source_type=source_filter)).distinct()

        indicator_rows = list(indicators)
        values = MEIndicatorValue.objects.filter(indicator__in=indicator_rows).select_related("indicator")
        if period_start:
            values = values.filter(period_end__gte=period_start)
        if period_end:
            values = values.filter(period_start__lte=period_end)
        approved_values = values.filter(approval_status="approved")
        values_by_indicator = {}
        for value in approved_values.order_by("indicator_id", "-period_end", "-updated_at"):
            values_by_indicator.setdefault(value.indicator_id, value)

        status_breakdown = {status_key: 0 for status_key, _label in MEIndicator._meta.get_field("status").choices}
        input_mode_breakdown = {"automatic": 0, "manual": 0, "imported": 0, "hybrid": 0}
        source_breakdown = {}
        ranking = []
        due_count = 0
        automated_count = 0
        alert_items = []
        trend_buckets = {}

        for indicator in indicator_rows:
            status_breakdown[indicator.status] = status_breakdown.get(indicator.status, 0) + 1
            input_mode_breakdown[indicator.input_mode] = input_mode_breakdown.get(indicator.input_mode, 0) + 1
            if indicator.input_mode in {"automatic", "hybrid"}:
                automated_count += 1
            source_key = indicator.data_source
            if source_key == "manual" and indicator.data_source_configs.exists():
                source_key = indicator.data_source_configs.first().source_type
            source_breakdown[source_key] = source_breakdown.get(source_key, 0) + 1

            latest = values_by_indicator.get(indicator.id)
            latest_number = None
            if latest:
                latest_number = latest.cumulative_value_numeric if latest.cumulative_value_numeric is not None else latest.progress_value_numeric
                month_key = latest.period_end.strftime("%Y-%m")
                trend_buckets.setdefault(month_key, {"period": month_key, "value": 0.0, "count": 0})
                if latest_number is not None:
                    trend_buckets[month_key]["value"] += float(latest_number)
                    trend_buckets[month_key]["count"] += 1
            target = indicator.target_value
            achievement = None
            if latest_number is not None and target:
                achievement = round((float(latest_number) / float(target)) * 100, 1)

            is_due = indicator.status == "active" and latest is None
            if is_due:
                due_count += 1
                alert_items.append({
                    "severity": "warning",
                    "title": "KPI due for reporting",
                    "detail": f"{indicator.indicator_code} has no approved value in the selected period.",
                    "indicator_id": str(indicator.id),
                })
            if achievement is not None and achievement < 60:
                alert_items.append({
                    "severity": "critical",
                    "title": "KPI below threshold",
                    "detail": f"{indicator.indicator_code} is at {achievement}% of target.",
                    "indicator_id": str(indicator.id),
                })
            ranking.append({
                "id": str(indicator.id),
                "name": indicator.indicator_name,
                "code": indicator.indicator_code,
                "status": indicator.status,
                "input_mode": indicator.input_mode,
                "data_source": source_key,
                "latest_value": str(latest_number) if latest_number is not None else None,
                "target": str(target) if target is not None else None,
                "achievement": achievement,
                "last_updated": latest.updated_at.isoformat() if latest else indicator.updated_at.isoformat(),
            })

        total = len(indicator_rows)
        active = status_breakdown.get("active", 0)
        data_completeness = round(((total - due_count) / total) * 100, 1) if total else 0
        ranking.sort(key=lambda row: (row["achievement"] is None, -(row["achievement"] or 0), row["name"]))
        trends = [
            {
                "period": period,
                "value": round(bucket["value"], 2),
                "count": bucket["count"],
            }
            for period, bucket in sorted(trend_buckets.items())
        ]

        state_comparison = _build_state_comparison(indicator_rows, approved_values)

        return Response({
            "summary_cards": [
                {"key": "total", "label": "Total KPIs", "value": total, "helper": "Configured Food Handler KPIs"},
                {"key": "active", "label": "Active KPIs", "value": active, "helper": "Currently reportable KPIs"},
                {"key": "due", "label": "Due for Reporting", "value": due_count, "helper": "Active KPIs without approved values"},
                {"key": "completeness", "label": "Data Completeness", "value": data_completeness, "suffix": "%", "helper": "KPIs with approved data"},
                {"key": "automatic", "label": "Automatic/Hybrid", "value": automated_count, "helper": "KPIs linked to operational sources"},
            ],
            "status_breakdown": status_breakdown,
            "input_mode_breakdown": input_mode_breakdown,
            "source_breakdown": source_breakdown,
            "rankings": ranking[:20],
            "trends": trends,
            "alerts": alert_items[:10],
            "state_comparison": state_comparison,
            "filters": {
                "period_start": period_start.isoformat() if period_start else "",
                "period_end": period_end.isoformat() if period_end else "",
                "status": status_filter or "",
                "input_mode": input_mode_filter or "",
                "data_source": source_filter or "",
                "state_id": state_id or "",
                "lga_id": lga_id or "",
            },
        })

    @action(detail=True, methods=["get", "post"], url_path="data-sources")
    def data_sources(self, request, pk=None):
        indicator = self.get_object()
        if request.method == "GET":
            return Response(MEIndicatorDataSourceSerializer(indicator.data_source_configs.all(), many=True).data)
        serializer = MEIndicatorDataSourceSerializer(data={**request.data, "indicator": str(indicator.id)})
        serializer.is_valid(raise_exception=True)
        source = MEIndicatorDataSource(indicator=indicator, **serializer.validated_data)
        errors = [
            *IndicatorIndicatorSourceAdapter.validate_indicator_source(source),
        ]
        if errors:
            return Response({"detail": errors[0], "errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        source.save()
        log_action(
            action=AuditAction.CREATE,
            actor=request.user,
            target=source,
            request=request,
            metadata={"event": "me_indicator_data_source_created", "indicator_id": str(indicator.id)},
        )
        return Response(MEIndicatorDataSourceSerializer(source).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="data-sources/forms")
    def link_form_source(self, request, pk=None):
        return Response(
            {"detail": "Form sources are not official Food Handlers KPI data sources. Use an operational data source such as registry, tests, certificates, facilities, inspections, training, payments, manual, or KPI dependencies."},
            status=status.HTTP_410_GONE,
        )

    @action(detail=True, methods=["post"], url_path="data-sources/indicators")
    def link_indicator_source(self, request, pk=None):
        indicator = self.get_object()
        serializer = MEIndicatorIndicatorSourceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        source = MEIndicatorDataSource(
            indicator=indicator,
            source_type="kpi",
            source_id="",
            calculation_method=data["calculation_method"],
            value_field_id="value",
            filter_config_json={
                "source_kpi_ids": [str(source_id) for source_id in data["source_kpi_ids"]],
            },
            period_filter_mode=data.get("period_filter_mode", "current_period"),
        )
        errors = IndicatorIndicatorSourceAdapter.validate_indicator_source(source)
        if errors:
            return Response({"detail": errors[0], "errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        source.save()
        log_action(
            action=AuditAction.CREATE,
            actor=request.user,
            target=source,
            request=request,
            metadata={"event": "me_indicator_source_indicators_linked", "indicator_id": str(indicator.id)},
        )
        return Response(MEIndicatorDataSourceSerializer(source).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="disaggregations")
    def disaggregations(self, request, pk=None):
        indicator = self.get_object()
        if request.method == "GET":
            return Response(IndicatorDisaggregationSerializer(indicator.disaggregations.all(), many=True).data)
        serializer = IndicatorDisaggregationSerializer(data={**request.data, "indicator": str(indicator.id)})
        serializer.is_valid(raise_exception=True)
        disaggregation = serializer.save(indicator=indicator)
        log_action(
            action=AuditAction.CREATE,
            actor=request.user,
            target=disaggregation,
            request=request,
            metadata={"event": "me_indicator_disaggregation_created", "indicator_id": str(indicator.id)},
        )
        return Response(IndicatorDisaggregationSerializer(disaggregation).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="values")
    def values(self, request, pk=None):
        indicator = self.get_object()
        if request.method == "GET":
            values = indicator.values.select_related(
                "indicator", "created_by", "submitted_by", "approved_by",
            ).prefetch_related("history")
            approval_status = request.query_params.get("approval_status")
            if approval_status:
                values = values.filter(approval_status=approval_status)
            return Response(MEIndicatorValueSerializer(values, many=True).data)

        serializer = MEIndicatorValueSerializer(data={**request.data, "indicator": str(indicator.id)})
        serializer.is_valid(raise_exception=True)
        value = serializer.save(indicator=indicator, created_by=request.user)
        create_indicator_value_history(value, request.user, "created", "", value.approval_status)
        log_action(
            action=AuditAction.CREATE,
            actor=request.user,
            target=value,
            request=request,
            metadata={"event": "me_indicator_value_created", "indicator_id": str(indicator.id)},
        )
        return Response(MEIndicatorValueSerializer(value).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="import-template")
    def import_template(self, request, pk=None):
        indicator = self.get_object()
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{indicator.indicator_code}-indicator-import-template.csv"'
        writer = csv.writer(response)
        writer.writerow(INDICATOR_IMPORT_COLUMNS)
        writer.writerow([
            indicator.indicator_code,
            "2026-01-01",
            "2026-03-31",
            "10",
            "10",
            "",
            "",
            "Imported historical value",
            "https://example.test/evidence.pdf",
        ])
        return response

    @action(detail=True, methods=["post"], url_path="import-preview")
    def import_preview(self, request, pk=None):
        indicator = self.get_object()
        rows, errors = preview_indicator_import(indicator, import_upload_text(request))
        valid_rows = [row for row in rows if row["valid"]]
        invalid_rows = [row for row in rows if not row["valid"]]
        return Response({
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "errors": errors,
            "summary": {
                "total": len(rows),
                "valid": len(valid_rows),
                "invalid": len(invalid_rows) + len(errors),
            },
        })

    @action(detail=True, methods=["post"], url_path="import-confirm")
    def import_confirm(self, request, pk=None):
        indicator = self.get_object()
        rows, errors = preview_indicator_import(indicator, import_upload_text(request))
        invalid_rows = [row for row in rows if not row["valid"]]
        if errors or invalid_rows:
            return Response({
                "detail": "Import contains invalid rows.",
                "invalid_rows": invalid_rows,
                "errors": errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        submit = str(request.data.get("submit", "")).lower() in {"1", "true", "yes"}
        imported = []
        with transaction.atomic():
            for row in rows:
                data = row["data"]
                serializer = MEIndicatorValueSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                value, created = MEIndicatorValue.objects.update_or_create(
                    indicator=indicator,
                    period_start=serializer.validated_data["period_start"],
                    period_end=serializer.validated_data["period_end"],
                    value_source="import",
                    source_reference_id=data["source_reference_id"],
                    defaults={
                        "progress_value_numeric": serializer.validated_data.get("progress_value_numeric"),
                        "cumulative_value_numeric": serializer.validated_data.get("cumulative_value_numeric"),
                        "qualitative_value_text": serializer.validated_data.get("qualitative_value_text", ""),
                        "qualitative_rating": serializer.validated_data.get("qualitative_rating"),
                        "qualitative_category": serializer.validated_data.get("qualitative_category", ""),
                        "evidence_json": serializer.validated_data.get("evidence_json", []),
                        "notes": serializer.validated_data.get("notes", ""),
                        "created_by": request.user,
                    },
                )
                if submit:
                    value.approval_status = "submitted"
                    value.submitted_by = request.user
                    value.submitted_at = timezone.now()
                    value.save(update_fields=["approval_status", "submitted_by", "submitted_at", "updated_at"])
                create_indicator_value_history(value, request.user, "imported" if created else "import_updated", "", value.approval_status)
                imported.append(value)

        log_action(
            action=AuditAction.CREATE,
            actor=request.user,
            target=indicator,
            request=request,
            metadata={"event": "me_indicator_values_imported", "indicator_id": str(indicator.id), "count": len(imported)},
        )
        return Response({
            "summary": {"imported": len(imported), "submitted": submit},
            "values": MEIndicatorValueSerializer(imported, many=True).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="evidence")
    def evidence(self, request, pk=None):
        indicator = self.get_object()
        if request.method == "GET":
            evidence_items = indicator.evidence.select_related("indicator", "indicator_value", "uploaded_by", "approved_by")
            approval_status = request.query_params.get("approval_status")
            if approval_status:
                evidence_items = evidence_items.filter(approval_status=approval_status)
            return Response(IndicatorEvidenceSerializer(evidence_items, many=True).data)
        serializer = IndicatorEvidenceSerializer(data={**request.data, "indicator": str(indicator.id)})
        serializer.is_valid(raise_exception=True)
        evidence = serializer.save(indicator=indicator, uploaded_by=request.user)
        log_action(
            action=AuditAction.CREATE,
            actor=request.user,
            target=evidence,
            request=request,
            metadata={"event": "indicator_evidence_created", "indicator_id": str(indicator.id)},
        )
        return Response(IndicatorEvidenceSerializer(evidence).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="calculate")
    def calculate(self, request, pk=None):
        indicator = self.get_object()
        if indicator.input_mode in {"automatic", "hybrid"}:
            filters = {
                "period_start": request.data.get("period_start"),
                "period_end": request.data.get("period_end"),
                "state_id": request.data.get("state_id"),
                "lga_id": request.data.get("lga_id"),
                "facility_id": request.data.get("facility_id"),
                "food_handler_category": request.data.get("food_handler_category"),
                "establishment_type": request.data.get("establishment_type"),
                "certificate_status": request.data.get("certificate_status"),
            }
            try:
                result = FoodHandlersKpiCalculationService.calculate_kpi(
                    indicator.id,
                    filters=filters,
                    actor=request.user,
                )
            except (KPIEngineError, ActivePolicyRuleError) as exc:
                return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            value = indicator.values.filter(id=result["value_id"]).first()
            if value is None:
                return Response({"detail": "Calculated KPI value could not be loaded."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            log_action(
                action=AuditAction.CREATE,
                actor=request.user,
                target=value,
                request=request,
                metadata={"event": "me_indicator_value_calculated", "indicator_id": str(indicator.id), "engine": "food_handlers_kpi"},
            )
            return Response(MEIndicatorValueSerializer(value).data, status=status.HTTP_201_CREATED)

        serializer = MEIndicatorCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        source = None
        if data.get("data_source_id"):
            source = indicator.data_source_configs.get(id=data["data_source_id"])
        else:
            source = MEIndicatorDataSource(
                indicator=indicator,
                source_type=data.get("source_type", "manual"),
                source_id=data.get("source_id", ""),
                calculation_method=data["calculation_method"],
                value_field_id=data.get("value_field_id", ""),
                numerator_config_json=data.get("numerator_config_json", {}),
                denominator_config_json=data.get("denominator_config_json", {}),
                filter_config_json=data.get("filter_config_json", {}),
                unicity_field_id=data.get("unicity_field_id", ""),
                period_filter_mode=data.get("period_filter_mode", "current_period"),
            )
        records = data.get("records") or source.filter_config_json.get("mock_records", [])
        period = {
            "period_start": data["period_start"].isoformat(),
            "period_end": data["period_end"].isoformat(),
        }
        try:
            result = IndicatorCalculationService.calculate(
                source,
                records,
                period,
                list(indicator.disaggregations.filter(source_type=source.source_type)),
            )
        except IndicatorCalculationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        value_source = "manual" if source.source_type == "manual" else "automated"
        source_reference_id = str(source.id) if source.id else source.source_id or "calculation"
        value, created = MEIndicatorValue.objects.update_or_create(
            indicator=indicator,
            period_start=data["period_start"],
            period_end=data["period_end"],
            value_source=value_source,
            source_reference_id=source_reference_id,
            defaults={
                "progress_value_numeric": result["value"],
                "cumulative_value_numeric": result["value"],
                "calculation_snapshot_json": result["snapshot"],
                "notes": "Generated by indicator calculation engine.",
                "created_by": request.user,
            },
        )
        value.disaggregated_values.all().delete()
        IndicatorDisaggregatedValue.objects.bulk_create([
            IndicatorDisaggregatedValue(
                indicator_value=value,
                indicator=indicator,
                period_start=data["period_start"],
                period_end=data["period_end"],
                dimension_values_json=row["dimension_values_json"],
                value_numeric=row["value_numeric"],
            )
            for row in result.get("disaggregations", [])
        ])
        create_indicator_value_history(value, request.user, "calculated" if created else "recalculated", "", value.approval_status)
        log_action(
            action=AuditAction.CREATE if created else AuditAction.UPDATE,
            actor=request.user,
            target=value,
            request=request,
            metadata={"event": "me_indicator_value_calculated", "indicator_id": str(indicator.id)},
        )
        return Response(MEIndicatorValueSerializer(value).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="recalculate")
    def recalculate(self, request, pk=None):
        indicator = self.get_object()
        if indicator.input_mode in {"automatic", "hybrid"}:
            return self.calculate(request, pk=pk)
        source = indicator.data_source_configs.exclude(source_type="manual").first()
        if not source:
            return Response({"detail": "No linked Food Handlers KPI data source is configured."}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        data["data_source_id"] = str(source.id)
        serializer = MEIndicatorCalculationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        request._full_data = data
        return self.calculate(request, pk=pk)

    @action(detail=True, methods=["get"], url_path="calculation")
    def calculation(self, request, pk=None):
        indicator = self.get_object()
        latest_log = indicator.calculation_logs.select_related("calculated_by", "policy_version").first()
        logs = indicator.calculation_logs.select_related("calculated_by", "policy_version")[:10]
        response = {
            "indicator_id": str(indicator.id),
            "indicator_name": indicator.indicator_name,
            "indicator_code": indicator.indicator_code,
            "input_mode": indicator.input_mode,
            "calculation_type": indicator.calculation_type,
            "calculation_source": indicator.calculation_source,
            "formula": indicator.calculation_type or indicator.formula_config.get("calculation_method", ""),
            "numerator_definition": indicator.numerator_definition or indicator.formula_config.get("numerator_definition") or indicator.formula_config.get("numerator") or {},
            "denominator_definition": indicator.denominator_definition or indicator.formula_config.get("denominator_definition") or indicator.formula_config.get("denominator") or {},
            "linked_policy_standard": indicator.policy_standard_code,
            "policy_rule_parameter": indicator.rule_parameter_key,
            "last_calculated_at": indicator.last_calculated_at,
            "latest_calculated_value": indicator.latest_value,
            "achievement_value": indicator.achievement_value,
            "latest_log": MEIndicatorCalculationLogSerializer(latest_log).data if latest_log else None,
            "logs": MEIndicatorCalculationLogSerializer(logs, many=True).data,
        }
        return Response(response)

    @action(detail=True, methods=["get"], url_path="source-records")
    def source_records(self, request, pk=None):
        indicator = self.get_object()
        filters = {
            "period_start": request.query_params.get("period_start"),
            "period_end": request.query_params.get("period_end"),
            "date_from": request.query_params.get("date_from"),
            "date_to": request.query_params.get("date_to"),
            "state_id": request.query_params.get("state_id"),
            "lga_id": request.query_params.get("lga_id"),
            "facility_id": request.query_params.get("facility_id"),
            "food_handler_category": request.query_params.get("food_handler_category"),
            "establishment_type": request.query_params.get("establishment_type"),
            "certificate_status": request.query_params.get("certificate_status"),
        }
        filters.update({
            key: value
            for key, value in scoped_kpi_filters_for_user(request.user).items()
            if not filters.get(key)
        })
        try:
            payload = FoodHandlersKpiCalculationService.get_kpi_source_records(indicator.id, filters=filters)
        except (KPIEngineError, ActivePolicyRuleError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        offset = max(int(request.query_params.get("offset", 0) or 0), 0)
        limit = min(max(int(request.query_params.get("limit", 25) or 25), 1), 200)
        records = payload["records"]
        page = records[offset:offset + limit]
        return Response({
            **payload,
            "count": len(records),
            "offset": offset,
            "limit": limit,
            "records": page,
            "has_next": offset + limit < len(records),
            "has_previous": offset > 0,
        })

    @action(detail=True, methods=["post"], url_path="override")
    def override(self, request, pk=None):
        indicator = self.get_object()
        if indicator.input_mode != "hybrid":
            return Response({"detail": "Only hybrid KPIs support manual override."}, status=status.HTTP_400_BAD_REQUEST)
        if not indicator.allow_manual_override:
            return Response({"detail": "Manual override is not enabled for this KPI."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MEIndicatorOverrideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if indicator.override_requires_reason and not data["reason"].strip():
            return Response({"detail": "Override reason is required."}, status=status.HTTP_400_BAD_REQUEST)

        calculated_value = indicator.values.filter(
            period_start=data["period_start"],
            period_end=data["period_end"],
            value_source="automated",
        ).order_by("-updated_at").first()
        if not calculated_value:
            return Response({"detail": "No calculated KPI value exists for the selected period."}, status=status.HTTP_400_BAD_REQUEST)

        override_value, created = MEIndicatorValue.objects.update_or_create(
            indicator=indicator,
            period_start=data["period_start"],
            period_end=data["period_end"],
            value_source="override",
            source_reference_id=str(calculated_value.id),
            defaults={
                "progress_value_numeric": data["override_value"],
                "cumulative_value_numeric": data["override_value"],
                "calculation_snapshot_json": {
                    **(calculated_value.calculation_snapshot_json or {}),
                    "override_applied": True,
                    "override_reason": data["reason"],
                    "original_value_id": str(calculated_value.id),
                    "original_value": str(calculated_value.cumulative_value_numeric or calculated_value.progress_value_numeric or ""),
                    "overridden_value": str(data["override_value"]),
                },
                "original_calculated_value": calculated_value.cumulative_value_numeric or calculated_value.progress_value_numeric,
                "overridden_value": data["override_value"],
                "override_reason": data["reason"],
                "overridden_by": request.user,
                "overridden_at": timezone.now(),
                "notes": data["reason"],
                "created_by": request.user,
            },
        )
        indicator.latest_value = data["override_value"]
        indicator.achievement_value = FoodHandlersKpiCalculationService.compute_achievement_value(indicator, data["override_value"])
        indicator.save(update_fields=["latest_value", "achievement_value", "updated_at"])
        create_indicator_value_history(
            override_value,
            request.user,
            "override",
            calculated_value.approval_status,
            override_value.approval_status,
            data["reason"],
        )
        indicator.calculation_logs.create(
            period_start=data["period_start"],
            period_end=data["period_end"],
            calculated_value=data["override_value"],
            numerator_value=calculated_value.original_calculated_value or calculated_value.cumulative_value_numeric or calculated_value.progress_value_numeric,
            denominator_value=None,
            filters_used={},
            policy_version=indicator.policy_version,
            policy_standard_code=indicator.policy_standard_code,
            policy_standard_id="",
            calculated_by=request.user,
            calculation_status=IndicatorCalculationStatus.OVERRIDDEN,
            error_message="",
            source_record_count=0,
            snapshot_json={
                "override_reason": data["reason"],
                "original_value_id": str(calculated_value.id),
                "original_value": str(calculated_value.cumulative_value_numeric or calculated_value.progress_value_numeric or ""),
                "overridden_value": str(data["override_value"]),
            },
        )
        log_action(
            action=AuditAction.UPDATE if not created else AuditAction.CREATE,
            actor=request.user,
            target=override_value,
            request=request,
            metadata={
                "event": "me_indicator_value_overridden",
                "indicator_id": str(indicator.id),
                "original_value_id": str(calculated_value.id),
                "override_reason": data["reason"],
            },
        )
        return Response(MEIndicatorValueSerializer(override_value).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


def indicator_value_snapshot(value):
    return {
        "period_start": value.period_start.isoformat(),
        "period_end": value.period_end.isoformat(),
        "progress_value_numeric": str(value.progress_value_numeric) if value.progress_value_numeric is not None else None,
        "cumulative_value_numeric": str(value.cumulative_value_numeric) if value.cumulative_value_numeric is not None else None,
        "qualitative_value_text": value.qualitative_value_text,
        "qualitative_rating": str(value.qualitative_rating) if value.qualitative_rating is not None else None,
        "approval_status": value.approval_status,
        "original_calculated_value": str(value.original_calculated_value) if value.original_calculated_value is not None else None,
        "overridden_value": str(value.overridden_value) if value.overridden_value is not None else None,
        "override_reason": value.override_reason,
        "notes": value.notes,
        "evidence_json": value.evidence_json,
    }


def create_indicator_value_history(value, actor, action, from_status, to_status, comment=""):
    return MEIndicatorValueHistory.objects.create(
        value=value,
        actor=actor,
        action=action,
        from_status=from_status or "",
        to_status=to_status or "",
        comment=comment or "",
        snapshot_json=indicator_value_snapshot(value),
    )


class MEIndicatorValueViewSet(viewsets.ModelViewSet):
    queryset = MEIndicatorValue.objects.all()
    serializer_class = MEIndicatorValueSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageStandards]
    http_method_names = ["get", "patch", "post", "head", "options"]
    filterset_fields = ["indicator", "approval_status", "value_source"]
    search_fields = ["indicator__indicator_name", "indicator__indicator_code", "notes"]

    def get_queryset(self):
        return MEIndicatorValue.objects.select_related(
            "indicator", "created_by", "submitted_by", "approved_by",
        ).prefetch_related("history", "disaggregated_values", "evidence_items")

    def partial_update(self, request, *args, **kwargs):
        value = self.get_object()
        if value.approval_status == "approved":
            return Response(
                {"detail": "Approved values cannot be edited directly. Create a revised draft value instead."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from_status = value.approval_status
        if value.approval_status == "rejected":
            mutable_data = request.data.copy()
            mutable_data["approval_status"] = "draft"
        else:
            mutable_data = request.data
        serializer = self.get_serializer(value, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        if from_status == "rejected":
            updated.approval_status = "draft"
            updated.rejection_comment = ""
            updated.save(update_fields=["approval_status", "rejection_comment", "updated_at"])
        create_indicator_value_history(updated, request.user, "updated", from_status, updated.approval_status)
        log_action(
            action=AuditAction.UPDATE,
            actor=request.user,
            target=updated,
            request=request,
            metadata={"event": "me_indicator_value_updated"},
        )
        return Response(self.get_serializer(updated).data)

    @action(detail=True, methods=["get", "post"], url_path="evidence")
    def evidence(self, request, pk=None):
        value = self.get_object()
        if request.method == "GET":
            evidence_items = value.evidence_items.select_related("indicator", "indicator_value", "uploaded_by", "approved_by")
            approval_status = request.query_params.get("approval_status")
            if approval_status:
                evidence_items = evidence_items.filter(approval_status=approval_status)
            return Response(IndicatorEvidenceSerializer(evidence_items, many=True).data)
        serializer = IndicatorEvidenceSerializer(data={
            **request.data,
            "indicator": str(value.indicator_id),
            "indicator_value": str(value.id),
        })
        serializer.is_valid(raise_exception=True)
        evidence = serializer.save(indicator=value.indicator, indicator_value=value, uploaded_by=request.user)
        log_action(
            action=AuditAction.CREATE,
            actor=request.user,
            target=evidence,
            request=request,
            metadata={"event": "indicator_value_evidence_created", "indicator_value_id": str(value.id)},
        )
        return Response(IndicatorEvidenceSerializer(evidence).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        value = self.get_object()
        if value.approval_status not in {"draft", "rejected"}:
            return Response({"detail": "Only draft or rejected values can be submitted."}, status=status.HTTP_400_BAD_REQUEST)
        from_status = value.approval_status
        value.approval_status = "submitted"
        value.submitted_by = request.user
        value.submitted_at = timezone.now()
        value.rejection_comment = ""
        value.save(update_fields=["approval_status", "submitted_by", "submitted_at", "rejection_comment", "updated_at"])
        create_indicator_value_history(value, request.user, "submitted", from_status, value.approval_status)
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=value,
            request=request,
            metadata={"event": "me_indicator_value_submitted"},
        )
        return Response(self.get_serializer(value).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        value = self.get_object()
        if value.approval_status != "submitted":
            return Response({"detail": "Only submitted values can be approved."}, status=status.HTTP_400_BAD_REQUEST)
        from_status = value.approval_status
        value.approval_status = "approved"
        value.approved_by = request.user
        value.approved_at = timezone.now()
        value.save(update_fields=["approval_status", "approved_by", "approved_at", "updated_at"])
        create_indicator_value_history(value, request.user, "approved", from_status, value.approval_status, request.data.get("comment", ""))
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=value,
            request=request,
            metadata={"event": "me_indicator_value_approved"},
        )
        return Response(self.get_serializer(value).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        value = self.get_object()
        if value.approval_status != "submitted":
            return Response({"detail": "Only submitted values can be rejected."}, status=status.HTTP_400_BAD_REQUEST)
        comment = request.data.get("comment", "").strip()
        if not comment:
            return Response({"detail": "A rejection comment is required."}, status=status.HTTP_400_BAD_REQUEST)
        from_status = value.approval_status
        value.approval_status = "rejected"
        value.rejection_comment = comment
        value.save(update_fields=["approval_status", "rejection_comment", "updated_at"])
        create_indicator_value_history(value, request.user, "rejected", from_status, value.approval_status, comment)
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=value,
            request=request,
            metadata={"event": "me_indicator_value_rejected"},
        )
        return Response(self.get_serializer(value).data)


class MEIndicatorDataSourceViewSet(viewsets.ModelViewSet):
    queryset = MEIndicatorDataSource.objects.all()
    serializer_class = MEIndicatorDataSourceSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageStandards]
    http_method_names = ["get", "patch", "delete", "head", "options"]
    filterset_fields = ["indicator", "source_type", "calculation_method", "period_filter_mode"]

    def partial_update(self, request, *args, **kwargs):
        source = self.get_object()
        serializer = self.get_serializer(source, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        preview = MEIndicatorDataSource(**{**{field.name: getattr(source, field.name) for field in source._meta.fields if field.name != "id"}, **serializer.validated_data})
        preview.id = source.id
        preview.indicator = source.indicator
        errors = [
            *IndicatorFormSourceAdapter.validate_form_source(preview),
            *IndicatorIndicatorSourceAdapter.validate_indicator_source(preview),
        ]
        if errors:
            return Response({"detail": errors[0], "errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        updated = serializer.save()
        log_action(
            action=AuditAction.UPDATE,
            actor=request.user,
            target=updated,
            request=request,
            metadata={"event": "me_indicator_data_source_updated"},
        )
        return Response(self.get_serializer(updated).data)


class IndicatorEvidenceViewSet(viewsets.ModelViewSet):
    queryset = IndicatorEvidence.objects.all()
    serializer_class = IndicatorEvidenceSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageStandards]
    http_method_names = ["get", "patch", "post", "head", "options"]
    filterset_fields = ["indicator", "indicator_value", "approval_status", "evidence_type"]
    search_fields = ["title", "description", "indicator__indicator_name", "indicator__indicator_code"]

    def get_queryset(self):
        return IndicatorEvidence.objects.select_related(
            "indicator", "indicator_value", "uploaded_by", "approved_by",
        )

    def partial_update(self, request, *args, **kwargs):
        evidence = self.get_object()
        if evidence.approval_status == "approved":
            return Response({"detail": "Approved evidence cannot be edited."}, status=status.HTTP_400_BAD_REQUEST)
        if evidence.approval_status == "rejected":
            mutable_data = request.data.copy()
            mutable_data["approval_status"] = "draft"
        else:
            mutable_data = request.data
        serializer = self.get_serializer(evidence, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        if evidence.approval_status == "rejected":
            updated.approval_status = "draft"
            updated.rejection_comment = ""
            updated.save(update_fields=["approval_status", "rejection_comment", "updated_at"])
        log_action(
            action=AuditAction.UPDATE,
            actor=request.user,
            target=updated,
            request=request,
            metadata={"event": "indicator_evidence_updated"},
        )
        return Response(self.get_serializer(updated).data)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        evidence = self.get_object()
        if evidence.approval_status not in {"draft", "rejected"}:
            return Response({"detail": "Only draft or rejected evidence can be submitted."}, status=status.HTTP_400_BAD_REQUEST)
        evidence.approval_status = "submitted"
        evidence.rejection_comment = ""
        evidence.save(update_fields=["approval_status", "rejection_comment", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=evidence,
            request=request,
            metadata={"event": "indicator_evidence_submitted"},
        )
        return Response(self.get_serializer(evidence).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        evidence = self.get_object()
        if evidence.approval_status != "submitted":
            return Response({"detail": "Only submitted evidence can be approved."}, status=status.HTTP_400_BAD_REQUEST)
        evidence.approval_status = "approved"
        evidence.approved_by = request.user
        evidence.approved_at = timezone.now()
        evidence.rejection_comment = ""
        evidence.save(update_fields=["approval_status", "approved_by", "approved_at", "rejection_comment", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=evidence,
            request=request,
            metadata={"event": "indicator_evidence_approved"},
        )
        return Response(self.get_serializer(evidence).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        evidence = self.get_object()
        if evidence.approval_status != "submitted":
            return Response({"detail": "Only submitted evidence can be rejected."}, status=status.HTTP_400_BAD_REQUEST)
        comment = request.data.get("comment", "").strip()
        if not comment:
            return Response({"detail": "A rejection comment is required."}, status=status.HTTP_400_BAD_REQUEST)
        evidence.approval_status = "rejected"
        evidence.rejection_comment = comment
        evidence.save(update_fields=["approval_status", "rejection_comment", "updated_at"])
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=evidence,
            request=request,
            metadata={"event": "indicator_evidence_rejected"},
        )
        return Response(self.get_serializer(evidence).data)


class PolicyDocumentViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = PolicyDocument.objects.all()
    serializer_class = PolicyDocumentSerializer
    filterset_fields = ["policy_version", "status", "document_type"]
    search_fields = ["title"]

    def perform_create(self, serializer):
        instance = serializer.save(uploaded_by=self.request.user)
        log_action(
            action=AuditAction.CREATE,
            actor=self.request.user,
            target=instance,
            metadata={"event": "policy_document_uploaded"},
            request=self.request,
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        document = self.get_object()
        if document.status != "draft":
            return Response(
                {"detail": "Only draft documents can be published."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        document.status = "published"
        document.published_by = request.user
        document.published_at = timezone.now()
        document.save()
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=document,
            metadata={"event": "policy_document_published"},
            request=request,
        )
        return Response(PolicyDocumentSerializer(document).data)

    @action(detail=True, methods=["post"])
    def retire(self, request, pk=None):
        document = self.get_object()
        if document.status != "published":
            return Response(
                {"detail": "Only published documents can be retired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        document.status = "retired"
        document.save()
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=document,
            old_value={"status": "published"},
            new_value={"status": "retired"},
            metadata={"event": "policy_document_retired"},
            request=request,
        )
        return Response(PolicyDocumentSerializer(document).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        document = self.get_object()
        if document.status not in {"draft", "retired"}:
            return Response(
                {"detail": "Only draft or retired documents can be archived."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        old_status = document.status
        document.status = "archived"
        document.save()
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=document,
            old_value={"status": old_status},
            new_value={"status": "archived"},
            metadata={"event": "policy_document_archived"},
            request=request,
        )
        return Response(PolicyDocumentSerializer(document).data)


class StateConfigurationControlViewSet(StandardsConfigViewSetMixin, viewsets.ModelViewSet):
    queryset = StateConfigurationControl.objects.all()
    serializer_class = StateConfigurationControlSerializer
    filterset_fields = ["policy_version", "federal_locked", "state_editable"]
    search_fields = ["config_domain", "label"]


class ApprovalViewSet(viewsets.ModelViewSet):
    queryset = Approval.objects.all()
    serializer_class = ApprovalSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageStandards]
    http_method_names = ["get", "head", "options"]
    filterset_fields = ["status", "impact_level", "entity_type"]
    search_fields = ["entity_type"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        qs = Approval.objects.select_related(
            "requested_by", "reviewer", "approver",
        )
        if user.role in FEDERAL_STANDARDS_ROLES:
            return qs
        return qs.none()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsActiveUser, CanApprovePolicyVersion])
    def approve(self, request, pk=None):
        approval = self.get_object()
        if approval.status != ApprovalStatus.PENDING:
            return Response(
                {"detail": "Only pending approvals can be approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = ApprovalActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        if approval.entity_type == "PolicyVersion":
            policy_version = PolicyVersion.objects.filter(id=approval.entity_id).first()
            if not policy_version:
                return Response({"detail": "Policy version not found."}, status=status.HTTP_404_NOT_FOUND)
            try:
                PolicyVersionService.approve(
                    policy_version=policy_version,
                    user=request.user,
                    comment=ser.validated_data.get("comment", ""),
                    request=request,
                )
            except ValueError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            approval.refresh_from_db()
            return Response(ApprovalSerializer(approval).data)

        approval.approver = request.user
        approval.status = ApprovalStatus.APPROVED
        approval.approval_comment = ser.validated_data.get("comment", "")
        approval.approved_at = timezone.now()
        approval.save()
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=approval,
            metadata={"event": "approval_approved"},
            request=request,
        )
        return Response(ApprovalSerializer(approval).data)

    @action(detail=True, methods=["post"], url_path="return", permission_classes=[IsAuthenticated, IsActiveUser, CanApprovePolicyVersion])
    def return_approval(self, request, pk=None):
        approval = self.get_object()
        if approval.status != ApprovalStatus.PENDING:
            return Response(
                {"detail": "Only pending approvals can be returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = ApprovalActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        comment = ser.validated_data.get("comment", "")
        if not comment:
            return Response(
                {"detail": "A comment is required when returning an approval."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if approval.entity_type == "PolicyVersion":
            policy_version = PolicyVersion.objects.filter(id=approval.entity_id).first()
            if not policy_version:
                return Response({"detail": "Policy version not found."}, status=status.HTTP_404_NOT_FOUND)
            try:
                PolicyVersionService.return_for_correction(
                    policy_version=policy_version,
                    user=request.user,
                    comment=comment,
                    request=request,
                )
            except ValueError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            approval.refresh_from_db()
            return Response(ApprovalSerializer(approval).data)

        approval.reviewer = request.user
        approval.status = ApprovalStatus.RETURNED
        approval.review_comment = comment
        approval.reviewed_at = timezone.now()
        approval.save()
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=approval,
            metadata={"event": "approval_returned"},
            request=request,
        )
        return Response(ApprovalSerializer(approval).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsActiveUser, CanApprovePolicyVersion])
    def reject(self, request, pk=None):
        approval = self.get_object()
        if approval.status != ApprovalStatus.PENDING:
            return Response(
                {"detail": "Only pending approvals can be rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = ApprovalActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        comment = ser.validated_data.get("comment", "")
        if not comment:
            return Response(
                {"detail": "A comment is required when rejecting an approval."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if approval.entity_type == "PolicyVersion":
            policy_version = PolicyVersion.objects.filter(id=approval.entity_id).first()
            if not policy_version:
                return Response({"detail": "Policy version not found."}, status=status.HTTP_404_NOT_FOUND)
            try:
                PolicyVersionService.reject(
                    policy_version=policy_version,
                    user=request.user,
                    comment=comment,
                    request=request,
                )
            except ValueError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            approval.refresh_from_db()
            return Response(ApprovalSerializer(approval).data)

        approval.reviewer = request.user
        approval.status = ApprovalStatus.REJECTED
        approval.review_comment = comment
        approval.reviewed_at = timezone.now()
        approval.save()
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=approval,
            metadata={"event": "approval_rejected"},
            request=request,
        )
        return Response(ApprovalSerializer(approval).data)


class StandardsAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = StandardsAuditLogSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanViewStandardsAudit]
    http_method_names = ["get", "head", "options"]

    standards_target_types = {
        "Approval",
        "CertificateTemplate",
        "CertificateValidityRule",
        "EstablishmentCategory",
        "FacilityRequirementRule",
        "FoodHandlerCategory",
        "MEIndicator",
        "MedicalTestRule",
        "PhysicalExaminationRule",
        "PolicyDocument",
        "PolicyVersion",
        "ReportingTemplate",
        "ReturnToWorkRule",
        "StateAcknowledgement",
        "StateConfigurationControl",
        "VaccinationRule",
    }

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        qs = AuditLog.objects.select_related("actor", "organization", "state").filter(
            target_type__in=self.standards_target_types,
        ).order_by("-created_at")

        action_value = self.request.query_params.get("action", "")
        target_type = self.request.query_params.get("target_type", "")
        target_id = self.request.query_params.get("target_id", "")
        actor = self.request.query_params.get("actor", "")
        policy_version = self.request.query_params.get("policy_version", "")
        date_from = self.request.query_params.get("date_from", "")
        date_to = self.request.query_params.get("date_to", "")
        search = self.request.query_params.get("search", "")

        if action_value:
            qs = qs.filter(action=action_value)
        if target_type:
            qs = qs.filter(target_type=target_type)
        if target_id:
            qs = qs.filter(target_id=target_id)
        if actor:
            qs = qs.filter(actor_id=actor)
        if policy_version:
            qs = qs.filter(Q(target_id=policy_version) | Q(metadata__icontains=policy_version))
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        if search:
            qs = qs.filter(
                Q(actor__email__icontains=search)
                | Q(actor__first_name__icontains=search)
                | Q(actor__last_name__icontains=search)
                | Q(action__icontains=search)
                | Q(target_type__icontains=search)
                | Q(target_id__icontains=search)
                | Q(metadata__icontains=search)
            )
        return qs

    @action(detail=False, methods=["get"])
    def export(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="standards-change-history.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "Created At",
            "Actor",
            "Actor Email",
            "Action",
            "Target Type",
            "Target ID",
            "Event",
            "State",
            "IP Address",
        ])
        for log in self.filter_queryset(self.get_queryset())[:1000]:
            metadata = log.metadata if isinstance(log.metadata, dict) else {}
            writer.writerow([
                log.created_at.isoformat(),
                log.actor.get_full_name() if log.actor else "System",
                log.actor.email if log.actor else "",
                log.action,
                log.target_type,
                log.target_id,
                metadata.get("event", ""),
                log.state.name if log.state else "National",
                log.ip_address or "",
            ])
        return response


class StateAcknowledgementViewSet(viewsets.ModelViewSet):
    queryset = StateAcknowledgement.objects.all()
    serializer_class = StateAcknowledgementSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanAcknowledgePolicy]
    http_method_names = ["get", "post", "head", "options"]
    filterset_fields = ["policy_version", "status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        qs = StateAcknowledgement.objects.select_related(
            "policy_version", "state", "acknowledged_by",
        )
        if user.role in FEDERAL_STANDARDS_ROLES:
            return qs
        if user.role == "state_admin" and user.state:
            return qs.filter(state=user.state)
        return qs.none()

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        ack = self.get_object()
        if ack.status == AcknowledgementStatus.ACKNOWLEDGED:
            return Response(
                {"detail": "Already acknowledged."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.role != "state_admin":
            return Response(
                {"detail": "Only State admins can acknowledge policy versions."},
                status=status.HTTP_403_FORBIDDEN,
            )
        ack.acknowledged_by = request.user
        ack.acknowledgement_comment = request.data.get("comment", "")
        ack.acknowledged_at = timezone.now()
        ack.status = AcknowledgementStatus.ACKNOWLEDGED
        ack.save()
        log_action(
            action=AuditAction.WORKFLOW_TRANSITION,
            actor=request.user,
            target=ack,
            metadata={
                "event": "policy_acknowledged",
                "state": str(ack.state_id),
                "policy_version": str(ack.policy_version_id),
            },
            request=request,
        )
        return Response(StateAcknowledgementSerializer(ack).data)


class ActiveStandardsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsActiveUser]
    cache_timeout = 300

    def _cache_key(self, suffix):
        version = cache.get(ACTIVE_STANDARDS_CACHE_VERSION_KEY, 1)
        return f"standards:active:v{version}:{suffix}"

    def _cached_response(self, suffix, builder):
        key = self._cache_key(suffix)
        payload = cache.get(key)
        if payload is None:
            payload = builder()
            cache.set(key, payload, self.cache_timeout)
        return Response(payload)

    def _get_active_policy(self):
        return PolicyVersion.objects.filter(
            status=PolicyVersionStatus.ACTIVE,
        ).first()

    def list(self, request):
        policy = self._get_active_policy()
        if not policy:
            return Response({"detail": "No active policy version."}, status=status.HTTP_404_NOT_FOUND)
        return self._cached_response("policy", lambda: PolicyVersionSerializer(policy).data)

    @action(detail=False, methods=["get"], url_path="handler-categories")
    def handler_categories(self, request):
        policy = self._get_active_policy()
        if not policy:
            return Response({"detail": "No active policy version."}, status=status.HTTP_404_NOT_FOUND)
        return self._cached_response(
            "handler-categories",
            lambda: FoodHandlerCategorySerializer(
                FoodHandlerCategory.objects.filter(policy_version=policy, status="active"),
                many=True,
            ).data,
        )

    @action(detail=False, methods=["get"], url_path="establishment-categories")
    def establishment_categories(self, request):
        policy = self._get_active_policy()
        if not policy:
            return Response({"detail": "No active policy version."}, status=status.HTTP_404_NOT_FOUND)
        return self._cached_response(
            "establishment-categories",
            lambda: EstablishmentCategorySerializer(
                EstablishmentCategory.objects.filter(policy_version=policy, status="active"),
                many=True,
            ).data,
        )

    @action(detail=False, methods=["get"], url_path="medical-tests")
    def medical_tests(self, request):
        policy = self._get_active_policy()
        if not policy:
            return Response({"detail": "No active policy version."}, status=status.HTTP_404_NOT_FOUND)
        qs = MedicalTestRule.objects.filter(
            policy_version=policy, status="active",
        )
        category_id = request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(applicable_categories__contains=[category_id])
        return self._cached_response(
            f"medical-tests:{category_id or 'all'}",
            lambda: MedicalTestRuleSerializer(qs, many=True).data,
        )

    @action(detail=False, methods=["get"], url_path="physical-examination-rules")
    def physical_examination_rules(self, request):
        policy = self._get_active_policy()
        if not policy:
            return Response({"detail": "No active policy version."}, status=status.HTTP_404_NOT_FOUND)
        return self._cached_response(
            "physical-examination-rules",
            lambda: PhysicalExaminationRuleSerializer(
                PhysicalExaminationRule.objects.filter(policy_version=policy, status="active"),
                many=True,
            ).data,
        )

    @action(detail=False, methods=["get"], url_path="vaccination-rules")
    def vaccination_rules(self, request):
        policy = self._get_active_policy()
        if not policy:
            return Response({"detail": "No active policy version."}, status=status.HTTP_404_NOT_FOUND)
        qs = VaccinationRule.objects.filter(
            policy_version=policy, status="active",
        )
        category_id = request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(applicable_categories__contains=[category_id])
        return self._cached_response(
            f"vaccination-rules:{category_id or 'all'}",
            lambda: VaccinationRuleSerializer(qs, many=True).data,
        )

    @action(detail=False, methods=["get"], url_path="certificate-template")
    def certificate_template(self, request):
        policy = self._get_active_policy()
        if not policy:
            return Response({"detail": "No active policy version."}, status=status.HTTP_404_NOT_FOUND)
        template = CertificateTemplate.objects.filter(
            policy_version=policy, status="active",
        ).first()
        if not template:
            return Response({"detail": "No active certificate template."}, status=status.HTTP_404_NOT_FOUND)
        return self._cached_response("certificate-template", lambda: CertificateTemplateSerializer(template).data)

    @action(detail=False, methods=["get"], url_path="certificate-validity-rules")
    def certificate_validity_rules(self, request):
        policy = self._get_active_policy()
        if not policy:
            return Response({"detail": "No active policy version."}, status=status.HTTP_404_NOT_FOUND)
        return self._cached_response(
            "certificate-validity-rules",
            lambda: CertificateValidityRuleSerializer(
                CertificateValidityRule.objects.filter(policy_version=policy, status="active"),
                many=True,
            ).data,
        )

    @action(detail=False, methods=["get"], url_path="return-to-work-rules")
    def return_to_work_rules(self, request):
        policy = self._get_active_policy()
        if not policy:
            return Response({"detail": "No active policy version."}, status=status.HTTP_404_NOT_FOUND)
        return self._cached_response(
            "return-to-work-rules",
            lambda: ReturnToWorkRuleSerializer(
                ReturnToWorkRule.objects.filter(policy_version=policy, status="active"),
                many=True,
            ).data,
        )

    @action(detail=False, methods=["get"], url_path="facility-requirements")
    def facility_requirements(self, request):
        policy = self._get_active_policy()
        if not policy:
            return Response({"detail": "No active policy version."}, status=status.HTTP_404_NOT_FOUND)
        return self._cached_response(
            "facility-requirements",
            lambda: FacilityRequirementRuleSerializer(
                FacilityRequirementRule.objects.filter(policy_version=policy, status="active"),
                many=True,
            ).data,
        )

    @action(detail=False, methods=["get"], url_path="reporting-template")
    def reporting_template(self, request):
        policy = self._get_active_policy()
        if not policy:
            return Response({"detail": "No active policy version."}, status=status.HTTP_404_NOT_FOUND)
        template = ReportingTemplate.objects.filter(
            policy_version=policy, status="active",
        ).first()
        if not template:
            return Response({"detail": "No active reporting template."}, status=status.HTTP_404_NOT_FOUND)
        return self._cached_response("reporting-template", lambda: ReportingTemplateSerializer(template).data)

    @action(detail=False, methods=["get"], url_path="me-indicators")
    def me_indicators(self, request):
        policy = self._get_active_policy()
        if not policy:
            return Response({"detail": "No active policy version."}, status=status.HTTP_404_NOT_FOUND)
        return self._cached_response(
            "me-indicators",
            lambda: MEIndicatorSerializer(
                MEIndicator.objects.filter(policy_version=policy, status="active"),
                many=True,
            ).data,
        )

    @action(detail=False, methods=["get"], url_path="state-configuration-controls")
    def state_configuration_controls(self, request):
        policy = self._get_active_policy()
        if not policy:
            return Response({"detail": "No active policy version."}, status=status.HTTP_404_NOT_FOUND)
        return self._cached_response(
            "state-configuration-controls",
            lambda: StateConfigurationControlSerializer(
                StateConfigurationControl.objects.filter(policy_version=policy),
                many=True,
            ).data,
        )
