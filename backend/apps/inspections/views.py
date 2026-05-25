from drf_spectacular.utils import extend_schema
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.certificates.models import Certificate, CertificateVerificationLog, SuspiciousCertificateReport, VerificationActorType, VerificationResult
from apps.certificates.services import CertificateService
from apps.inspections.models import Inspection, InspectionCertificateScan
from apps.inspections.serializers import (
    CertificateScanSerializer,
    CreateInspectionSerializer,
    InspectorCertificateFlagSerializer,
    InspectorCertificateNumberSerializer,
    InspectorCertificateSaveSerializer,
    InspectorCertificateVerificationSerializer,
    InspectionCertificateScanSerializer,
    InspectionEvidenceSerializer,
    InspectionSerializer,
)
from apps.inspections.services import InspectionService


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
