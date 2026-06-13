from drf_spectacular.utils import extend_schema
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.certificates.models import Certificate, CertificateVerificationLog, SuspiciousCertificateReport, VerificationActorType, VerificationResult
from apps.certificates.services import CertificateService
from apps.forms.models import FormPrimaryModule, FormTemplate, FormTemplatePurpose, FormTemplateStatus
from apps.forms.serializers import FormAssignmentSerializer, FormResponseSerializer, FormTemplateSerializer
from apps.inspections.models import (
    CorrectiveActionResponse,
    CorrectiveActionStatus,
    EnforcementCase,
    EnforcementNotice,
    Inspection,
    InspectionCertificateScan,
    InspectionChecklistItem,
    InspectionChecklistResponse,
    InspectionEvidence,
    InspectionFinding,
    NoticeStatus,
)
from apps.inspections.serializers import (
    CertificateScanSerializer,
    CorrectiveActionResponseCreateSerializer,
    CorrectiveActionResponseSerializer,
    CreateInspectionSerializer,
    EnforcementCaseSerializer,
    EnforcementNoticeCreateSerializer,
    EnforcementNoticeSerializer,
    InspectionChecklistItemSerializer,
    InspectionChecklistResponseSerializer,
    InspectionEvidenceSerializer,
    InspectionFindingCreateSerializer,
    InspectionFindingSerializer,
    InspectionResponseSerializer,
    InspectorCertificateFlagSerializer,
    InspectorCertificateNumberSerializer,
    InspectorCertificateSaveSerializer,
    InspectorCertificateVerificationSerializer,
    InspectionCertificateScanSerializer,
    InspectionSerializer,
)
from apps.inspections.services import InspectionService, InspectionDashboardService


def _ensure_inspector(user):
    if user.role not in {UserRole.INSPECTOR, UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN}:
        raise PermissionDenied("Only inspectors or regulators can verify certificates here.")


def _inspector_certificate_response(request, lookup):
    _ensure_inspector(request.user)
    certificate = Certificate.objects.select_related("food_handler", "assessment", "facility", "issuing_state").filter(
        Q(certificate_number=lookup) | Q(verification_token=lookup)
    ).first()
    if not certificate:
        CertificateVerificationLog.objects.create(
            certificate_number_submitted=lookup,
            result=VerificationResult.NOT_FOUND,
            verifier_type=VerificationActorType.INSPECTOR,
            verifier_user=request.user,
            ip_address=request.META.get("REMOTE_ADDR", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        log_action(
            action=AuditAction.PUBLIC_VERIFICATION,
            actor=request.user,
            target_type="Certificate",
            target_id="",
            metadata={"event": "inspector_certificate_verified", "lookup": lookup, "result": VerificationResult.NOT_FOUND},
        )
        return Response({"certificate_validity": VerificationResult.NOT_FOUND, "certificate_number": lookup}, status=404)
    result = CertificateService.verification_result_for(certificate)
    CertificateVerificationLog.objects.create(
        certificate=certificate,
        certificate_number_submitted=certificate.certificate_number,
        verification_token_submitted=lookup if lookup == certificate.verification_token else "",
        result=result,
        verifier_type=VerificationActorType.INSPECTOR,
        verifier_user=request.user,
        ip_address=request.META.get("REMOTE_ADDR", ""),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    log_action(
        action=AuditAction.PUBLIC_VERIFICATION,
        actor=request.user,
        target=certificate,
        metadata={"event": "inspector_certificate_verified", "result": result},
    )
    return Response(InspectorCertificateVerificationSerializer(certificate, context={"verification_result": result}).data)


class InspectionViewSet(viewsets.ModelViewSet):
    queryset = Inspection.objects.select_related("inspector", "employer", "employer__state", "branch").order_by("-inspection_date")
    serializer_class = InspectionSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["status", "enforcement_action", "employer", "branch", "inspector"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            queryset = self.queryset.filter(employer__state=user.state)
            if user.unit_id and getattr(user.unit, "lga_id", None):
                queryset = queryset.filter(employer__lga_id=user.unit.lga_id)
            return queryset
        if user.role == UserRole.EMPLOYER:
            if hasattr(user, "employer"):
                queryset = self.queryset.filter(employer=user.employer)
            elif user.organization_id:
                queryset = self.queryset.filter(employer__organization=user.organization)
            else:
                return self.queryset.none()
            if user.unit_restricted and user.unit_id:
                queryset = queryset.filter(branch=user.unit)
            return queryset
        return self.queryset.none()

    def get_serializer_class(self):
        if self.action in {"create", "partial_update"}:
            return CreateInspectionSerializer
        return InspectionSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateInspectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inspection = InspectionService.create(inspector=request.user, **serializer.validated_data)
        return Response(InspectionSerializer(inspection).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        serializer = CreateInspectionSerializer(instance=self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        inspection = InspectionService.update(inspection=self.get_object(), actor=request.user, **serializer.validated_data)
        return Response(InspectionSerializer(inspection).data)

    @extend_schema(responses=InspectionSerializer)
    @action(detail=True, methods=["patch"], url_path="submit")
    def submit(self, request, pk=None):
        inspection = InspectionService.submit(inspection=self.get_object(), actor=request.user)
        return Response(InspectionSerializer(inspection).data)

    @extend_schema(request=InspectionEvidenceSerializer, responses=InspectionSerializer)
    @action(detail=True, methods=["post"], url_path="evidence")
    def evidence(self, request, pk=None):
        serializer = InspectionEvidenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inspection = InspectionService.add_evidence(
            inspection=self.get_object(),
            actor=request.user,
            evidence=serializer.validated_data,
        )
        return Response(InspectionSerializer(inspection).data)

    def _inspection_template_queryset(self):
        queryset = (
            FormTemplate.objects.filter(status=FormTemplateStatus.PUBLISHED)
            .filter(Q(purpose=FormTemplatePurpose.INSPECTION_CHECKLIST) | Q(primary_module=FormPrimaryModule.INSPECTIONS))
            .order_by("title")
        )
        user = self.request.user
        if user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            if user.organization_id:
                queryset = queryset.filter(owner_organization=user.organization)
            elif user.state_id:
                queryset = queryset.filter(owner_organization__state=user.state)
        return queryset

    def _ensure_can_assign_form(self, inspection):
        if self.request.user.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only ministry administrators can assign inspection forms.")
        if self.request.user.role == UserRole.STATE_ADMIN and inspection.employer.state_id != self.request.user.state_id:
            raise PermissionDenied("You can only assign forms to inspections in your state.")

    def _ensure_can_submit_form(self, inspection):
        if self.request.user.role in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return
        if self.request.user.role == UserRole.INSPECTOR and inspection.inspector_id == self.request.user.id:
            return
        raise PermissionDenied("You cannot submit this inspection form.")

    @extend_schema(responses=dict)
    @action(detail=True, methods=["get"], url_path="form-response")
    def form_response(self, request, pk=None):
        inspection = self.get_object()
        form_response = InspectionService.inspection_form_workspace(inspection=inspection)
        payload = {
            "assignment": FormAssignmentSerializer(form_response.assignment).data if form_response else None,
            "response": FormResponseSerializer(form_response).data if form_response else None,
            "available_templates": FormTemplateSerializer(self._inspection_template_queryset(), many=True).data
            if request.user.role in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}
            else [],
        }
        return Response(payload)

    @extend_schema(responses=dict)
    @action(detail=True, methods=["post"], url_path="assign-form")
    def assign_form(self, request, pk=None):
        inspection = self.get_object()
        self._ensure_can_assign_form(inspection)
        template_id = request.data.get("form_template") or request.data.get("template") or request.data.get("template_id")
        if not template_id:
            raise ValidationError({"form_template": "Select an inspection form template."})
        template = self._inspection_template_queryset().filter(id=template_id).first()
        if not template:
            raise ValidationError({"form_template": "Select a published inspection form template."})
        assignment, form_response = InspectionService.assign_form_template(
            inspection=inspection,
            actor=request.user,
            template=template,
        )
        return Response(
            {
                "assignment": FormAssignmentSerializer(assignment).data,
                "response": FormResponseSerializer(form_response).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(responses=dict)
    @action(detail=True, methods=["post"], url_path="submit-form")
    def submit_form(self, request, pk=None):
        inspection = self.get_object()
        self._ensure_can_submit_form(inspection)
        response_json = request.data.get("response_json")
        if response_json is None:
            response_json = request.data.get("responses")
        if response_json is None:
            raise ValidationError({"response_json": "Submit the completed inspection form data."})
        form_response = InspectionService.submit_form_response(
            inspection=inspection,
            actor=request.user,
            response_json=response_json,
        )
        inspection.refresh_from_db()
        return Response(
            {
                "inspection": InspectionSerializer(inspection).data,
                "response": FormResponseSerializer(form_response).data,
            }
        )

    @extend_schema(request=CertificateScanSerializer, responses=InspectionCertificateScanSerializer)
    @action(detail=True, methods=["post"], url_path="scan-certificate")
    def scan_certificate(self, request, pk=None):
        serializer = CertificateScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        scan = InspectionService.scan_certificate(
            inspection=self.get_object(),
            actor=request.user,
            certificate_number=serializer.validated_data["certificate_number"],
        )
        return Response(InspectionCertificateScanSerializer(scan).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=InspectionSerializer)
    @action(detail=True, methods=["post"], url_path="accept")
    def accept(self, request, pk=None):
        inspection = InspectionService.accept(inspection=self.get_object(), actor=request.user)
        return Response(InspectionSerializer(inspection).data)

    @extend_schema(responses=InspectionSerializer)
    @action(detail=True, methods=["post"], url_path="start")
    def start(self, request, pk=None):
        inspection = InspectionService.start(inspection=self.get_object(), actor=request.user)
        return Response(InspectionSerializer(inspection).data)

    @extend_schema(responses=InspectionSerializer)
    @action(detail=True, methods=["post"], url_path="return-for-correction")
    def return_for_correction(self, request, pk=None):
        inspection = InspectionService.return_for_correction(inspection=self.get_object(), actor=request.user)
        return Response(InspectionSerializer(inspection).data)

    @extend_schema(responses=InspectionSerializer)
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        reason = request.data.get("reason", "")
        inspection = InspectionService.cancel(inspection=self.get_object(), actor=request.user, reason=reason)
        return Response(InspectionSerializer(inspection).data)

    @extend_schema(responses=InspectionSerializer)
    @action(detail=True, methods=["post"], url_path="reschedule-request")
    def reschedule_request(self, request, pk=None):
        reason = request.data.get("reason", "")
        inspection = InspectionService.reschedule_request(inspection=self.get_object(), actor=request.user, reason=reason)
        return Response(InspectionSerializer(inspection).data)

    @extend_schema(responses=InspectionSerializer)
    @action(detail=True, methods=["post"], url_path="create-follow-up")
    def create_follow_up(self, request, pk=None):
        parent = self.get_object()
        inspector_id = request.data.get("inspector_id")
        inspector = None
        if inspector_id:
            from apps.accounts.models import User
            inspector = User.objects.filter(id=inspector_id).first()
        scheduled_at = request.data.get("scheduled_at")
        reason = request.data.get("reason", "")
        follow_up = InspectionService.create_follow_up(
            parent_inspection=parent,
            actor=request.user,
            inspector=inspector,
            scheduled_at=scheduled_at,
            reason=reason,
        )
        return Response(InspectionSerializer(follow_up).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=EnforcementCaseSerializer)
    @action(detail=True, methods=["post"], url_path="escalate")
    def escalate(self, request, pk=None):
        inspection = self.get_object()
        severity = request.data.get("severity", "medium")
        summary = request.data.get("summary", "")
        enforcement_case = InspectionService.escalate_inspection(
            inspection=inspection,
            actor=request.user,
            severity=severity,
            summary=summary,
        )
        return Response(EnforcementCaseSerializer(enforcement_case).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=InspectionChecklistResponseSerializer(many=True))
    @action(detail=True, methods=["get", "post"], url_path="checklist-responses")
    def checklist_responses(self, request, pk=None):
        inspection = self.get_object()
        if request.method == "GET":
            responses = InspectionChecklistResponse.objects.filter(inspection=inspection).select_related("checklist_item")
            return Response(InspectionChecklistResponseSerializer(responses, many=True).data)
        serializer = InspectionChecklistResponseSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        item = serializer.validated_data["checklist_item"]
        resp_obj, _ = InspectionChecklistResponse.objects.update_or_create(
            inspection=inspection,
            checklist_item=item,
            defaults={
                "response": serializer.validated_data["response"],
                "severity": serializer.validated_data.get("severity", ""),
                "note": serializer.validated_data.get("note", ""),
                "created_by": request.user,
            },
        )
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=resp_obj, metadata={"event": "checklist_response_upserted"})
        return Response(InspectionChecklistResponseSerializer(resp_obj).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=InspectionChecklistResponseSerializer)
    @action(detail=True, methods=["patch"], url_path="checklist-responses/(?P<response_id>[^/.]+)")
    def update_checklist_response(self, request, pk=None, response_id=None):
        inspection = self.get_object()
        resp_obj = InspectionChecklistResponse.objects.filter(inspection=inspection, id=response_id).first()
        if not resp_obj:
            raise ValidationError("Checklist response not found.")
        serializer = InspectionChecklistResponseSerializer(resp_obj, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        if "severity" in serializer.validated_data:
            resp_obj.severity = serializer.validated_data["severity"]
        if "response" in serializer.validated_data:
            resp_obj.response = serializer.validated_data["response"]
        if "note" in serializer.validated_data:
            resp_obj.note = serializer.validated_data["note"]
        resp_obj.created_by = request.user
        resp_obj.save()
        return Response(InspectionChecklistResponseSerializer(resp_obj).data)

    @extend_schema(responses=InspectionFindingSerializer(many=True))
    @action(detail=True, methods=["get", "post"], url_path="findings")
    def findings(self, request, pk=None):
        inspection = self.get_object()
        if request.method == "GET":
            findings = InspectionFinding.objects.filter(inspection=inspection)
            return Response(InspectionFindingSerializer(findings, many=True).data)
        serializer = InspectionFindingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        finding = InspectionFinding.objects.create(
            inspection=inspection,
            created_by=request.user,
            **serializer.validated_data,
        )
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=finding, metadata={"event": "finding_created"})
        return Response(InspectionFindingSerializer(finding).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=InspectionFindingSerializer)
    @action(detail=True, methods=["get", "patch"], url_path="findings/(?P<finding_id>[^/.]+)")
    def finding_detail(self, request, pk=None, finding_id=None):
        inspection = self.get_object()
        finding = InspectionFinding.objects.filter(inspection=inspection, id=finding_id).first()
        if not finding:
            raise ValidationError("Finding not found.")
        if request.method == "GET":
            return Response(InspectionFindingSerializer(finding).data)
        serializer = InspectionFindingCreateSerializer(finding, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(finding, field, value)
        finding.save()
        return Response(InspectionFindingSerializer(finding).data)

    @extend_schema(responses={201: InspectionEvidenceSerializer})
    @action(detail=True, methods=["post"], url_path="evidence-upload")
    def evidence_upload(self, request, pk=None):
        inspection = self.get_object()
        serializer = InspectionEvidenceSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        evidence = InspectionEvidence.objects.create(
            inspection=inspection,
            uploaded_by=request.user,
            **{k: v for k, v in serializer.validated_data.items() if k != "inspection"},
        )
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=evidence, metadata={"event": "evidence_uploaded"})
        return Response(InspectionEvidenceSerializer(evidence).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=InspectionEvidenceSerializer(many=True))
    @action(detail=True, methods=["get"], url_path="evidence-entries")
    def evidence_entries(self, request, pk=None):
        inspection = self.get_object()
        evidence = InspectionEvidence.objects.filter(inspection=inspection)
        return Response(InspectionEvidenceSerializer(evidence, many=True).data)

    @extend_schema(responses={204: None})
    @action(detail=True, methods=["delete"], url_path="evidence-entries/(?P<evidence_id>[^/.]+)")
    def delete_evidence(self, request, pk=None, evidence_id=None):
        inspection = self.get_object()
        evidence = InspectionEvidence.objects.filter(inspection=inspection, id=evidence_id).first()
        if not evidence:
            raise ValidationError("Evidence not found.")
        evidence.delete()
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=inspection, metadata={"event": "evidence_deleted", "evidence_id": evidence_id})
        return Response(status=status.HTTP_204_NO_CONTENT)


class InspectionChecklistItemViewSet(viewsets.ModelViewSet):
    queryset = InspectionChecklistItem.objects.all()
    serializer_class = InspectionChecklistItemSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        queryset = self.queryset.filter(is_active=True).order_by("category", "sort_order")
        if not getattr(self, "swagger_fake_view", False) and self.request.user.role in {UserRole.INSPECTOR, UserRole.LGA_OFFICER}:
            return queryset
        return self.queryset.filter(is_active=True)

    def perform_create(self, serializer):
        if self.request.user.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDenied("Only state administrators can manage checklist items.")
        serializer.save()


class EnforcementNoticeViewSet(viewsets.ModelViewSet):
    queryset = EnforcementNotice.objects.select_related("inspection", "employer", "issued_by", "approved_by")
    serializer_class = EnforcementNoticeSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return self.queryset.filter(employer__state=user.state)
        if user.role == UserRole.EMPLOYER:
            if hasattr(user, "employer"):
                return self.queryset.filter(employer=user.employer)
            elif user.organization_id:
                return self.queryset.filter(employer__organization=user.organization)
            return self.queryset.none()
        return self.queryset.none()

    def get_serializer_class(self):
        if self.action == "create":
            return EnforcementNoticeCreateSerializer
        return EnforcementNoticeSerializer

    def perform_create(self, serializer):
        notice = serializer.save(
            issued_by=self.request.user,
            notice_reference=self._generate_notice_ref(),
        )
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=self.request.user, target=notice, metadata={"event": "notice_created"})

    def _generate_notice_ref(self):
        today = timezone.now()
        prefix = f"FCN-NOT-{today.year}"
        latest = (
            EnforcementNotice.objects.filter(notice_reference__startswith=prefix)
            .order_by("-notice_reference")
            .values_list("notice_reference", flat=True)
            .first()
        )
        seq = (int(latest.split("-")[-1]) + 1) if latest else 1
        return f"{prefix}-{seq:06d}"

    @action(detail=True, methods=["post"], url_path="submit-for-approval")
    def submit_for_approval(self, request, pk=None):
        notice = self.get_object()
        notice.status = NoticeStatus.PENDING_APPROVAL
        notice.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=notice, metadata={"event": "notice_submitted_for_approval"})
        return Response(EnforcementNoticeSerializer(notice).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        notice = self.get_object()
        if request.user.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDenied("Only state administrators can approve notices.")
        notice.status = NoticeStatus.ISSUED
        notice.approved_by = request.user
        notice.issued_at = timezone.now()
        notice.save(update_fields=["status", "approved_by", "issued_at", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=notice, metadata={"event": "notice_approved_and_issued"})
        return Response(EnforcementNoticeSerializer(notice).data)

    @action(detail=True, methods=["post"], url_path="acknowledge")
    def acknowledge(self, request, pk=None):
        notice = self.get_object()
        notice.status = NoticeStatus.ACKNOWLEDGED
        notice.acknowledged_at = timezone.now()
        notice.save(update_fields=["status", "acknowledged_at", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=notice, metadata={"event": "notice_acknowledged"})
        return Response(EnforcementNoticeSerializer(notice).data)

    @action(detail=True, methods=["post"], url_path="close")
    def close_notice(self, request, pk=None):
        notice = self.get_object()
        if request.user.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDenied("Only state administrators can close notices.")
        notice.status = NoticeStatus.CLOSED
        notice.closed_at = timezone.now()
        notice.closure_note = request.data.get("closure_note", "")
        notice.save(update_fields=["status", "closed_at", "closure_note", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=notice, metadata={"event": "notice_closed"})
        return Response(EnforcementNoticeSerializer(notice).data)

    @extend_schema(responses=CorrectiveActionResponseSerializer(many=True))
    @action(detail=True, methods=["get", "post"], url_path="corrective-actions")
    def corrective_actions(self, request, pk=None):
        notice = self.get_object()
        if request.method == "GET":
            responses = CorrectiveActionResponse.objects.filter(notice=notice)
            return Response(CorrectiveActionResponseSerializer(responses, many=True).data)
        serializer = CorrectiveActionResponseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resp = CorrectiveActionResponse.objects.create(
            notice=notice,
            submitted_by=request.user,
            response_note=serializer.validated_data["response_note"],
            action_taken=serializer.validated_data["action_taken"],
        )
        if notice.status == NoticeStatus.ISSUED or notice.status == NoticeStatus.ACKNOWLEDGED:
            notice.status = NoticeStatus.RESPONSE_SUBMITTED
            notice.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=resp, metadata={"event": "corrective_action_submitted"})
        return Response(CorrectiveActionResponseSerializer(resp).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="corrective-actions/(?P<response_id>[^/.]+)/review")
    def review_corrective_action(self, request, pk=None, response_id=None):
        notice = self.get_object()
        resp = CorrectiveActionResponse.objects.filter(notice=notice, id=response_id).first()
        if not resp:
            raise ValidationError("Response not found.")
        if request.user.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only ministry reviewers can review corrective actions.")
        action_type = request.data.get("action")
        if action_type == "accept":
            resp.status = CorrectiveActionStatus.ACCEPTED
        elif action_type == "reject":
            resp.status = CorrectiveActionStatus.REJECTED
        elif action_type == "request_more_evidence":
            resp.status = CorrectiveActionStatus.MORE_EVIDENCE_REQUESTED
        else:
            raise ValidationError("Invalid review action.")
        resp.reviewed_by = request.user
        resp.review_note = request.data.get("review_note", "")
        resp.reviewed_at = timezone.now()
        resp.save(update_fields=["status", "reviewed_by", "review_note", "reviewed_at", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=resp, metadata={"event": "corrective_action_reviewed", "review_action": action_type})
        return Response(CorrectiveActionResponseSerializer(resp).data)


class EnforcementCaseViewSet(viewsets.ModelViewSet):
    queryset = EnforcementCase.objects.select_related("state", "employer", "opened_by", "assigned_to")
    serializer_class = EnforcementCaseSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["status", "severity", "state", "employer"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return self.queryset.filter(state=user.state)
        if user.role == UserRole.EMPLOYER:
            if hasattr(user, "employer"):
                return self.queryset.filter(employer=user.employer)
            elif user.organization_id:
                return self.queryset.filter(employer__organization=user.organization)
            return self.queryset.none()
        return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only coordinators can create enforcement cases.")
        serializer.save(
            opened_by=user,
            state=serializer.validated_data.get("state", user.state),
            case_reference=self._generate_case_ref(),
        )

    def _generate_case_ref(self):
        today = timezone.now()
        prefix = f"FCN-CASE-{today.year}"
        latest = (
            EnforcementCase.objects.filter(case_reference__startswith=prefix)
            .order_by("-case_reference")
            .values_list("case_reference", flat=True)
            .first()
        )
        seq = (int(latest.split("-")[-1]) + 1) if latest else 1
        return f"{prefix}-{seq:06d}"

    @action(detail=True, methods=["post"], url_path="close")
    def close_case(self, request, pk=None):
        instance = self.get_object()
        if request.user.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only authorized users can close enforcement cases.")
        instance.status = "closed"
        instance.closure_note = request.data.get("closure_note", "")
        instance.closed_at = timezone.now()
        instance.save(update_fields=["status", "closure_note", "closed_at", "updated_at"])
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=instance, metadata={"event": "enforcement_case_closed"})
        return Response(EnforcementCaseSerializer(instance).data)

    @action(detail=True, methods=["post"], url_path="escalate")
    def escalate_case(self, request, pk=None):
        instance = self.get_object()
        reason = request.data.get("reason", "")
        enforcement_case = InspectionService.escalate_case(
            enforcement_case=instance,
            actor=request.user,
            reason=reason,
        )
        return Response(EnforcementCaseSerializer(enforcement_case).data)


@extend_schema(responses=InspectorCertificateVerificationSerializer)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsActiveUser])
def inspector_verify_certificate(request, verification_code):
    return _inspector_certificate_response(request, verification_code)


@extend_schema(request=InspectorCertificateNumberSerializer, responses=InspectorCertificateVerificationSerializer)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsActiveUser])
def inspector_verify_certificate_by_number(request):
    serializer = InspectorCertificateNumberSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return _inspector_certificate_response(request, serializer.validated_data["certificate_number"].strip())


@extend_schema(request=InspectorCertificateSaveSerializer, responses=InspectionCertificateScanSerializer)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsActiveUser])
def inspector_save_certificate_to_inspection(request, certificate_id):
    _ensure_inspector(request.user)
    serializer = InspectorCertificateSaveSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    inspection = serializer.validated_data["inspection"]
    if request.user.role != UserRole.SUPER_ADMIN and inspection.employer.state_id != request.user.state_id:
        raise PermissionDenied("You can only save verification results to inspections in your state.")
    certificate = Certificate.objects.filter(id=certificate_id).first()
    if not certificate:
        raise ValidationError("Certificate not found.")
    result = CertificateService.verification_result_for(certificate)
    scan = InspectionCertificateScan.objects.create(
        inspection=inspection,
        certificate=certificate,
        certificate_number=certificate.certificate_number,
        result=result,
    )
    log_action(action=AuditAction.PUBLIC_VERIFICATION, actor=request.user, target=scan, metadata={"event": "inspection_certificate_verification_saved", "result": result})
    return Response(InspectionCertificateScanSerializer(scan).data, status=status.HTTP_201_CREATED)


@extend_schema(request=InspectorCertificateFlagSerializer)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsActiveUser])
def inspector_flag_certificate(request, certificate_id):
    _ensure_inspector(request.user)
    serializer = InspectorCertificateFlagSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    certificate = Certificate.objects.filter(id=certificate_id).first()
    if not certificate:
        raise ValidationError("Certificate not found.")
    report = SuspiciousCertificateReport.objects.create(
        certificate=certificate,
        certificate_number_submitted=certificate.certificate_number,
        verification_token_submitted=certificate.verification_token or "",
        reporter_name=request.user.get_full_name() or request.user.email,
        reporter_contact=request.user.email,
        reason=serializer.validated_data["reason"],
        details=serializer.validated_data.get("details", ""),
        ip_address=request.META.get("REMOTE_ADDR", ""),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    log_action(
        action=AuditAction.CERTIFICATE_EVENT,
        actor=request.user,
        target=certificate,
        metadata={"event": "inspector_certificate_flagged", "report_id": str(report.id), "reason": report.reason},
    )
    return Response({"status": "flagged", "report_id": str(report.id)}, status=status.HTTP_201_CREATED)


class InspectorDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        if request.user.role not in {UserRole.INSPECTOR, UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only inspectors and regulators can access this dashboard.")
        return Response(InspectionDashboardService.inspector_dashboard(request.user))


class InspectorTasksView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        if request.user.role not in {UserRole.INSPECTOR, UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDenied("Only inspector roles can access tasks.")
        inspections = InspectionDashboardService.inspector_tasks(
            request.user,
            status_filter=request.query_params.get("status"),
            priority=request.query_params.get("priority"),
            inspection_type=request.query_params.get("inspection_type"),
            scheduled_from=request.query_params.get("scheduled_from"),
            scheduled_to=request.query_params.get("scheduled_to"),
        )
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(inspections, request, view=self)
        serializer = InspectionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class InspectionEmployerContextView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request, pk):
        inspection = Inspection.objects.filter(id=pk).first()
        if not inspection:
            raise ValidationError("Inspection not found.")
        return Response(InspectionDashboardService.employer_context(inspection))


class InspectionComplianceSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request, pk):
        inspection = Inspection.objects.filter(id=pk).first()
        if not inspection:
            raise ValidationError("Inspection not found.")
        return Response(InspectionDashboardService.compliance_summary(inspection))


class InspectionFoodHandlersView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request, pk):
        inspection = Inspection.objects.filter(id=pk).first()
        if not inspection:
            raise ValidationError("Inspection not found.")
        return Response(InspectionDashboardService.food_handlers_for_inspection(inspection))


class StateEnforcementDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        if request.user.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDenied("Only state administrators can access the state enforcement dashboard.")
        return Response(InspectionDashboardService.state_enforcement_dashboard(
            request.user,
            lga_id=request.query_params.get("lga_id"),
            date_from=request.query_params.get("date_from"),
            date_to=request.query_params.get("date_to"),
        ))


class StateEnforcementReportsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request, report_type):
        if request.user.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDenied("Only state administrators can view enforcement reports.")
        return Response({"report_type": report_type, "data": []})


class FederalEnforcementDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        if request.user.role not in {UserRole.FEDERAL_ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDenied("Only federal administrators can access the federal enforcement dashboard.")
        return Response(InspectionDashboardService.federal_enforcement_dashboard(request.user))


class FederalEnforcementReportsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        if request.user.role not in {UserRole.FEDERAL_ADMIN, UserRole.SUPER_ADMIN}:
            raise PermissionDenied("Only federal administrators can view enforcement reports.")
        return Response({"reports": [], "filters": {}})


class StateInspectionsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def _ensure_state_admin(self, user):
        if user.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only state ministry administrators can manage inspections.")

    def _base_queryset(self, user):
        qs = Inspection.objects.select_related(
            "inspector", "employer", "employer__state", "employer__lga", "branch", "assigned_by"
        ).prefetch_related("employer_responses")
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return qs
        return qs.filter(employer__state=user.state)

    def _serialize(self, inspection, include_detail=False):
        from apps.audit.models import AuditLog
        payload = InspectionSerializer(inspection).data
        payload["state_name"] = inspection.employer.state.name if inspection.employer.state else None
        payload["lga_name"] = inspection.employer.lga.name if inspection.employer.lga else None
        payload["responses"] = InspectionResponseSerializer(
            inspection.employer_responses.select_related("submitted_by").order_by("-submitted_at"), many=True
        ).data
        audit_logs = AuditLog.objects.filter(
            target_type="Inspection", target_id=str(inspection.id)
        ).select_related("actor").order_by("-created_at")[:20]
        payload["audit_history"] = [
            {
                "id": str(log.id),
                "action": log.action,
                "actor_name": log.actor.get_full_name() if log.actor else None,
                "metadata": log.metadata or {},
                "created_at": log.created_at.isoformat(),
            }
            for log in audit_logs
        ]
        if include_detail:
            form_response = InspectionService.inspection_form_workspace(inspection=inspection)
            payload["form_response"] = FormResponseSerializer(form_response).data if form_response else None
            payload["form_assignment"] = FormAssignmentSerializer(form_response.assignment).data if form_response else None
        return payload

    def get(self, request):
        self._ensure_state_admin(request.user)
        qs = self._base_queryset(request.user)
        queue = request.query_params.get("queue")
        if queue == "active":
            qs = qs.exclude(status__in=[InspectionStatus.CLOSED, InspectionStatus.CANCELLED])
        elif queue == "submitted":
            qs = qs.filter(status=InspectionStatus.SUBMITTED)
        elif queue == "enforcement":
            qs = qs.exclude(enforcement_action="none")
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        enforcement = request.query_params.get("enforcement_action")
        if enforcement:
            qs = qs.filter(enforcement_action=enforcement)
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(employer__business_name__icontains=search)
                | Q(inspector__first_name__icontains=search)
                | Q(inspector__last_name__icontains=search)
                | Q(findings__icontains=search)
                | Q(reference__icontains=search)
            )
        inspector = request.query_params.get("inspector")
        if inspector:
            qs = qs.filter(inspector_id=inspector)
        employer = request.query_params.get("employer")
        if employer:
            qs = qs.filter(employer_id=employer)
        qs = qs.order_by("-inspection_date")[:200]
        return Response([self._serialize(inspection) for inspection in qs])

    def post(self, request):
        self._ensure_state_admin(request.user)
        serializer = CreateInspectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inspector_id = request.data.get("inspector")
        if not inspector_id:
            raise ValidationError({"inspector": "Select an inspector."})
        from apps.accounts.models import User as UserModel
        inspector = UserModel.objects.filter(id=inspector_id, role=UserRole.INSPECTOR).first()
        if not inspector:
            raise ValidationError({"inspector": "Inspector not found."})
        inspection = InspectionService.assign(
            actor=request.user,
            inspector=inspector,
            **serializer.validated_data,
        )
        form_template_id = request.data.get("form_template")
        if form_template_id:
            template = FormTemplate.objects.filter(
                id=form_template_id, status=FormTemplateStatus.PUBLISHED
            ).first()
            if template:
                InspectionService.assign_form_template(
                    inspection=inspection, actor=request.user, template=template
                )
        return Response(self._serialize(inspection), status=status.HTTP_201_CREATED)


class StateInspectionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def _ensure_state_admin(self, user):
        if user.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only state ministry administrators can view inspections.")

    def get(self, request, pk):
        self._ensure_state_admin(request.user)
        inspection = Inspection.objects.select_related(
            "inspector", "employer", "employer__state", "employer__lga", "branch", "assigned_by"
        ).prefetch_related("employer_responses").filter(id=pk).first()
        if not inspection:
            raise ValidationError("Inspection not found.")
        if request.user.role == UserRole.STATE_ADMIN and inspection.employer.state_id != request.user.state_id:
            raise PermissionDenied("You can only view inspections in your state.")
        view = StateInspectionsView()
        return Response(view._serialize(inspection, include_detail=True))


class StateInspectionReviewView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def patch(self, request, pk):
        if request.user.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only state ministry administrators can review inspections.")
        inspection = Inspection.objects.select_related(
            "inspector", "employer", "employer__state", "employer__lga", "branch"
        ).prefetch_related("employer_responses").filter(id=pk).first()
        if not inspection:
            raise ValidationError("Inspection not found.")
        if request.user.role == UserRole.STATE_ADMIN and inspection.employer.state_id != request.user.state_id:
            raise PermissionDenied("You can only review inspections in your state.")
        kwargs = {}
        if "enforcement_action" in request.data:
            kwargs["enforcement_action"] = request.data["enforcement_action"]
        if "findings" in request.data:
            kwargs["findings"] = request.data["findings"]
        if "checklist_responses" in request.data:
            kwargs["checklist_responses"] = request.data["checklist_responses"]
        if "evidence_files" in request.data:
            kwargs["evidence_files"] = request.data["evidence_files"]
        inspection = InspectionService.review(inspection=inspection, actor=request.user, **kwargs)
        view = StateInspectionsView()
        return Response(view._serialize(inspection, include_detail=True))


class StateInspectionCloseView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def patch(self, request, pk):
        if request.user.role not in {UserRole.STATE_ADMIN, UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only state ministry administrators can close inspections.")
        inspection = Inspection.objects.select_related(
            "inspector", "employer", "employer__state", "employer__lga", "branch"
        ).prefetch_related("employer_responses").filter(id=pk).first()
        if not inspection:
            raise ValidationError("Inspection not found.")
        if request.user.role == UserRole.STATE_ADMIN and inspection.employer.state_id != request.user.state_id:
            raise PermissionDenied("You can only close inspections in your state.")
        closure_notes = request.data.get("closure_notes", "")
        inspection = InspectionService.close(inspection=inspection, actor=request.user, closure_notes=closure_notes)
        view = StateInspectionsView()
        return Response(view._serialize(inspection, include_detail=True))
