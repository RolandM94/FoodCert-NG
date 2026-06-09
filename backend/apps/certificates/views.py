from django.http import FileResponse
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.decorators import throttle_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.assessments.models import MedicalAssessment
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.common.throttles import PublicVerificationRateThrottle, SuspiciousReportRateThrottle
from apps.certificates.models import AccreditationCertificate, Certificate, CertificateRequest, CertificateTemplate, CertificateTemplateScope, CertificateVerificationLog, SuspiciousCertificateReport, VerificationActorType, VerificationResult
from apps.certificates.serializers import (
    AccreditationCertificatePublicVerificationSerializer,
    AccreditationCertificateSerializer,
    CertificatePublicVerificationSerializer,
    CertificateRequestSerializer,
    CertificateSerializer,
    CertificateStatusChangeSerializer,
    CertificateTemplateSerializer,
    EmployerCertificateSerializer,
    FoodHandlerCertificateSerializer,
    GenerateCertificateSerializer,
    PublicCertificateNumberVerificationSerializer,
    RequestCertificateSerializer,
    ReviewCertificateRequestSerializer,
    SuspiciousCertificateReportSerializer,
)
from apps.certificates.services import CertificateService
from apps.notifications.models import Notification, NotificationCategory
from apps.policy.models import NationalPolicyConfig


class CertificateRequestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CertificateRequest.objects.select_related(
        "assessment",
        "assessment__food_handler",
        "assessment__facility",
        "assessment__facility__state",
        "requested_by",
        "reviewed_by",
    ).order_by("-created_at")
    serializer_class = CertificateRequestSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["status", "assessment__facility__state", "assessment__facility"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return self.queryset.filter(assessment__facility__state=user.state)
        if user.role == UserRole.FOOD_HANDLER:
            return self.queryset.filter(assessment__food_handler__user=user)
        if user.role == UserRole.EMPLOYER and hasattr(user, "employer"):
            return self.queryset.filter(assessment__employer=user.employer)
        if user.organization_id:
            return self.queryset.filter(assessment__facility__organization=user.organization)
        return self.queryset.none()

    @extend_schema(request=ReviewCertificateRequestSerializer, responses=CertificateRequestSerializer)
    @action(detail=True, methods=["patch"], url_path="approve")
    def approve(self, request, pk=None):
        serializer = ReviewCertificateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate_request = CertificateService.approve_request(
            request=self.get_object(),
            reviewer=request.user,
            notes=serializer.validated_data.get("review_notes", ""),
        )
        return Response(CertificateRequestSerializer(certificate_request).data)

    @extend_schema(request=ReviewCertificateRequestSerializer, responses=CertificateRequestSerializer)
    @action(detail=True, methods=["patch"], url_path="request-clarification")
    def request_clarification(self, request, pk=None):
        serializer = ReviewCertificateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notes = serializer.validated_data.get("review_notes", "")
        if not notes.strip():
            raise ValidationError("Review notes are required when requesting clarification.")
        certificate_request = CertificateService.request_clarification(
            request=self.get_object(),
            reviewer=request.user,
            notes=notes,
        )
        return Response(CertificateRequestSerializer(certificate_request).data)

    @extend_schema(request=ReviewCertificateRequestSerializer, responses=CertificateRequestSerializer)
    @action(detail=True, methods=["patch"], url_path="reject")
    def reject(self, request, pk=None):
        serializer = ReviewCertificateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate_request = CertificateService.reject_request(
            request=self.get_object(),
            reviewer=request.user,
            notes=serializer.validated_data.get("review_notes", ""),
        )
        return Response(CertificateRequestSerializer(certificate_request).data)


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Certificate.objects.select_related(
        "food_handler",
        "assessment",
        "employer",
        "facility",
        "doctor",
        "issuing_state",
        "issued_by_state_user",
        "revoked_by",
    ).order_by("-issue_date", "-created_at")
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["status", "issuing_state", "facility", "food_handler"]

    def get_serializer_class(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return CertificateSerializer
        if self.request.user.role == UserRole.EMPLOYER:
            return EmployerCertificateSerializer
        if self.request.user.role == UserRole.FOOD_HANDLER:
            return FoodHandlerCertificateSerializer
        return CertificateSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return self.queryset.filter(issuing_state=user.state)
        if user.role == UserRole.FOOD_HANDLER:
            return self.queryset.filter(food_handler__user=user)
        if user.role == UserRole.EMPLOYER:
            if hasattr(user, "employer"):
                queryset = self.queryset.filter(employer=user.employer)
            elif user.organization_id:
                queryset = self.queryset.filter(employer__organization=user.organization)
            else:
                return self.queryset.none()
            if user.unit_restricted and user.unit_id:
                queryset = queryset.filter(food_handler__business_branch=user.unit)
            return queryset
        if user.organization_id:
            return self.queryset.filter(facility__organization=user.organization)
        return self.queryset.none()

    @extend_schema(responses=CertificateSerializer)
    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        certificate = self.get_object()
        certificate.pdf_url = CertificateService.write_pdf(certificate=certificate)
        certificate.save(update_fields=["pdf_url", "updated_at"])
        media_prefix = "http://localhost:8000/media/"
        relative_path = certificate.pdf_url.replace(media_prefix, "")
        file_path = str(settings.MEDIA_ROOT / relative_path)
        event = "food_handler_certificate_download" if request.user.role == UserRole.FOOD_HANDLER else "certificate_download"
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=request.user, target=certificate, metadata={"event": event})
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=f"{certificate.certificate_number}.pdf")

    @extend_schema(request=CertificateStatusChangeSerializer, responses=CertificateSerializer)
    @action(detail=True, methods=["patch"], url_path="revoke")
    def revoke(self, request, pk=None):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("Only regulators can revoke certificates.")
        serializer = CertificateStatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate = CertificateService.revoke(
            certificate=self.get_object(),
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(CertificateSerializer(certificate).data)

    @extend_schema(request=CertificateStatusChangeSerializer, responses=CertificateSerializer)
    @action(detail=True, methods=["patch"], url_path="suspend")
    def suspend(self, request, pk=None):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("Only regulators can suspend certificates.")
        serializer = CertificateStatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate = CertificateService.suspend(
            certificate=self.get_object(),
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(CertificateSerializer(certificate).data)

    @extend_schema(responses=FoodHandlerCertificateSerializer)
    @action(detail=True, methods=["post"], url_path="start-renewal")
    def start_renewal(self, request, pk=None):
        certificate = self.get_object()
        if request.user.role != UserRole.FOOD_HANDLER or certificate.food_handler.user_id != request.user.id:
            raise PermissionDenied("Only the certificate owner can start renewal.")
        Notification.objects.create(
            recipient=request.user,
            category=NotificationCategory.RENEWAL,
            title="Certificate renewal started",
            message="Start a fresh medical assessment to renew this certificate.",
        )
        log_action(
            action=AuditAction.CERTIFICATE_EVENT,
            actor=request.user,
            target=certificate,
            metadata={"event": "certificate_renewal_started", "next_url": "/food-handler/assessments"},
        )
        return Response(FoodHandlerCertificateSerializer(certificate).data)


class AccreditationCertificateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AccreditationCertificateSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        queryset = AccreditationCertificate.objects.select_related(
            "employer",
            "facility",
            "issuing_state",
            "issued_by_state_user",
        ).order_by("-issue_date", "-created_at")
        if getattr(self, "swagger_fake_view", False):
            return queryset
        certificate_type = self.request.query_params.get("certificate_type")
        if certificate_type:
            queryset = queryset.filter(certificate_type=certificate_type)
        employer = self.request.query_params.get("employer")
        if employer:
            queryset = queryset.filter(employer_id=employer)
        facility = self.request.query_params.get("facility")
        if facility:
            queryset = queryset.filter(facility_id=facility)
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return queryset.filter(issuing_state=user.state)
        if user.role == UserRole.EMPLOYER:
            if hasattr(user, "employer"):
                return queryset.filter(employer=user.employer)
            if user.organization_id:
                return queryset.filter(employer__organization=user.organization)
            return queryset.none()
        if user.organization_id:
            return queryset.filter(facility__organization=user.organization)
        return queryset.none()

    @extend_schema(responses=AccreditationCertificateSerializer)
    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        certificate = self.get_object()
        certificate.pdf_url = CertificateService.write_accreditation_pdf(certificate=certificate)
        certificate.save(update_fields=["pdf_url", "updated_at"])
        media_prefix = "http://localhost:8000/media/"
        relative_path = certificate.pdf_url.replace(media_prefix, "")
        file_path = str(settings.MEDIA_ROOT / relative_path)
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=request.user, target=certificate, metadata={"event": "accreditation_certificate_download"})
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=f"{certificate.certificate_number}.pdf")


class CertificateTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = CertificateTemplateSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        queryset = CertificateTemplate.objects.select_related("state", "created_by").order_by("scope", "state__name", "-is_default", "name")
        if getattr(self, "swagger_fake_view", False):
            return queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return queryset
        if user.role == UserRole.STATE_ADMIN and user.state_id:
            return queryset.filter(Q(scope=CertificateTemplateScope.NATIONAL) | Q(scope=CertificateTemplateScope.STATE, state=user.state))
        return queryset.none()

    def _state_templates_allowed(self):
        policy = NationalPolicyConfig.objects.order_by("-updated_at").first()
        return True if policy is None else policy.state_certificate_template_overrides_enabled

    def _ensure_can_manage(self, template=None, attrs=None):
        user = self.request.user
        scope = (attrs or {}).get("scope") or getattr(template, "scope", CertificateTemplateScope.NATIONAL)
        state = (attrs or {}).get("state") if attrs and "state" in attrs else getattr(template, "state", None)
        if user.role == UserRole.SUPER_ADMIN:
            return
        if scope == CertificateTemplateScope.NATIONAL:
            if user.role == UserRole.FEDERAL_ADMIN:
                return
            raise PermissionDenied("Only federal admins can manage national certificate templates.")
        if user.role != UserRole.STATE_ADMIN:
            raise PermissionDenied("Only state admins can manage state certificate templates.")
        if not self._state_templates_allowed():
            raise PermissionDenied("State certificate template overrides are disabled by national policy.")
        if not user.state_id or not state or state.id != user.state_id:
            raise PermissionDenied("State admins can only manage templates for their own state.")

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if request.user.role == UserRole.STATE_ADMIN and data.get("scope", CertificateTemplateScope.STATE) == CertificateTemplateScope.STATE:
            data["scope"] = CertificateTemplateScope.STATE
            data["state"] = str(request.user.state_id)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        self._ensure_can_manage(attrs=serializer.validated_data)
        template = serializer.save(created_by=self.request.user)
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=self.request.user, target=template, metadata={"event": "certificate_template_created"})

    def perform_update(self, serializer):
        self._ensure_can_manage(template=self.get_object(), attrs=serializer.validated_data)
        template = serializer.save()
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=self.request.user, target=template, metadata={"event": "certificate_template_updated"})

    def perform_destroy(self, instance):
        self._ensure_can_manage(template=instance)
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=self.request.user, target=instance, metadata={"event": "certificate_template_deleted"})
        instance.delete()

    @action(detail=True, methods=["post"], url_path="set-default")
    def set_default(self, request, pk=None):
        template = self.get_object()
        self._ensure_can_manage(template=template)
        if not template.is_active:
            raise ValidationError("Only active templates can be set as default.")
        CertificateTemplate.objects.filter(scope=template.scope, state=template.state).exclude(id=template.id).update(is_default=False)
        template.is_default = True
        template.save(update_fields=["is_default", "updated_at"])
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=request.user, target=template, metadata={"event": "certificate_template_set_default"})
        return Response(CertificateTemplateSerializer(template).data)


class RequestCertificateView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=RequestCertificateSerializer, responses={201: CertificateRequestSerializer})
    def post(self, request, assessment_id):
        assessment = get_object_or_404(MedicalAssessment.objects.select_related("food_handler", "facility", "doctor", "payment_transaction"), id=assessment_id)
        serializer = RequestCertificateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate_request = CertificateService.request_certificate(
            assessment=assessment,
            actor=request.user,
            notes=serializer.validated_data.get("request_notes", ""),
        )
        return Response(CertificateRequestSerializer(certificate_request).data, status=status.HTTP_201_CREATED)


class GenerateCertificateView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=GenerateCertificateSerializer, responses={201: CertificateSerializer})
    def post(self, request):
        serializer = GenerateCertificateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate_request = serializer.validated_data.get("certificate_request")
        assessment = serializer.validated_data.get("assessment") or certificate_request.assessment
        try:
            certificate = CertificateService.issue_certificate(assessment=assessment, actor=request.user)
        except Exception as exc:
            log_action(
                action=AuditAction.CERTIFICATE_EVENT,
                actor=request.user,
                target=certificate_request or assessment,
                metadata={"event": "certificate_generation_failed", "reason": str(exc)[:240]},
            )
            raise
        return Response(CertificateSerializer(certificate).data, status=status.HTTP_201_CREATED)


@extend_schema(responses=CertificatePublicVerificationSerializer)
@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([PublicVerificationRateThrottle])
def public_verify_certificate(request, certificate_number):
    return _public_verify_certificate_response(request, certificate_number)


def _public_verify_certificate_response(request, certificate_number):
    certificate = Certificate.objects.filter(Q(certificate_number=certificate_number) | Q(verification_token=certificate_number)).select_related(
        "food_handler",
        "assessment",
        "facility",
        "issuing_state",
    ).first()
    result = VerificationResult.NOT_FOUND
    if certificate:
        result = CertificateService.verification_result_for(certificate)
    accreditation_certificate = None
    if not certificate:
        accreditation_certificate = AccreditationCertificate.objects.filter(
            Q(certificate_number=certificate_number) | Q(verification_token=certificate_number)
        ).select_related("employer", "facility", "issuing_state").first()
        if accreditation_certificate:
            result = CertificateService.accreditation_verification_result_for(accreditation_certificate)
    CertificateVerificationLog.objects.create(
        certificate=certificate,
        certificate_number_submitted=certificate_number,
        verification_token_submitted=certificate_number if certificate and certificate.verification_token == certificate_number else "",
        result=result,
        ip_address=request.META.get("REMOTE_ADDR", ""),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    log_action(
        action=AuditAction.PUBLIC_VERIFICATION,
        target=certificate,
        target_type="Certificate",
        target_id=str(certificate.id) if certificate else "",
        request=request,
        metadata={"certificate_number": certificate_number, "result": result},
    )
    if not certificate and not accreditation_certificate:
        return Response({"certificate_validity": VerificationResult.NOT_FOUND, "certificate_number": certificate_number}, status=404)
    if accreditation_certificate:
        payload = AccreditationCertificatePublicVerificationSerializer(accreditation_certificate).data
        payload["certificate_validity"] = result
        return Response(payload)
    payload = CertificatePublicVerificationSerializer(certificate).data
    payload["certificate_validity"] = result
    return Response(payload)


@extend_schema(request=PublicCertificateNumberVerificationSerializer, responses=CertificatePublicVerificationSerializer)
@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([PublicVerificationRateThrottle])
def public_verify_certificate_by_number(request):
    serializer = PublicCertificateNumberVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    certificate_number = serializer.validated_data["certificate_number"].strip()
    return _public_verify_certificate_response(request, certificate_number)


@extend_schema(request=SuspiciousCertificateReportSerializer, responses={201: SuspiciousCertificateReportSerializer})
@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([SuspiciousReportRateThrottle])
def public_report_suspicious_certificate(request):
    serializer = SuspiciousCertificateReportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    certificate_number = serializer.validated_data.get("certificate_number", "").strip()
    verification_token = serializer.validated_data.get("verification_token", "").strip()
    certificate = Certificate.objects.filter(
        Q(certificate_number=certificate_number) | Q(verification_token=verification_token)
    ).first()
    report = SuspiciousCertificateReport.objects.create(
        certificate=certificate,
        certificate_number_submitted=certificate_number,
        verification_token_submitted=verification_token,
        reporter_name=serializer.validated_data.get("reporter_name", ""),
        reporter_contact=serializer.validated_data.get("reporter_contact", ""),
        reason=serializer.validated_data["reason"],
        details=serializer.validated_data.get("details", ""),
        ip_address=request.META.get("REMOTE_ADDR", ""),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    CertificateVerificationLog.objects.create(
        certificate=certificate,
        certificate_number_submitted=certificate_number,
        verification_token_submitted=verification_token,
        result=CertificateService.verification_result_for(certificate) if certificate else VerificationResult.NOT_FOUND,
        verifier_type=VerificationActorType.PUBLIC,
        ip_address=request.META.get("REMOTE_ADDR", ""),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    log_action(
        action=AuditAction.CERTIFICATE_EVENT,
        target=certificate or report,
        target_type="SuspiciousCertificateReport",
        target_id=str(report.id),
        request=request,
        metadata={
            "event": "suspicious_certificate_reported",
            "certificate_number": certificate_number,
            "verification_token_provided": bool(verification_token),
        },
    )
    return Response(SuspiciousCertificateReportSerializer(report).data, status=status.HTTP_201_CREATED)
