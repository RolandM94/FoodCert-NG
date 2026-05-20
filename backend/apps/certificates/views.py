from django.http import FileResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.decorators import throttle_classes
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.assessments.models import MedicalAssessment
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.common.throttles import PublicVerificationRateThrottle
from apps.certificates.models import Certificate, CertificateRequest, CertificateVerificationLog, VerificationResult
from apps.certificates.serializers import (
    CertificatePublicVerificationSerializer,
    CertificateRequestSerializer,
    CertificateSerializer,
    CertificateStatusChangeSerializer,
    EmployerCertificateSerializer,
    GenerateCertificateSerializer,
    RequestCertificateSerializer,
    ReviewCertificateRequestSerializer,
)
from apps.certificates.services import CertificateService


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
        if not certificate.pdf_url:
            raise NotFound("Certificate PDF is not available.")
        media_prefix = "http://localhost:8000/media/"
        relative_path = certificate.pdf_url.replace(media_prefix, "")
        file_path = str(settings.MEDIA_ROOT / relative_path)
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
        certificate = CertificateService.issue_certificate(assessment=assessment, actor=request.user)
        return Response(CertificateSerializer(certificate).data, status=status.HTTP_201_CREATED)


@extend_schema(responses=CertificatePublicVerificationSerializer)
@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([PublicVerificationRateThrottle])
def public_verify_certificate(request, certificate_number):
    certificate = Certificate.objects.filter(certificate_number=certificate_number).select_related(
        "food_handler",
        "assessment",
        "facility",
        "issuing_state",
    ).first()
    result = VerificationResult.NOT_FOUND
    if certificate:
        result = CertificateService.verification_result_for(certificate)
    CertificateVerificationLog.objects.create(
        certificate=certificate,
        certificate_number_submitted=certificate_number,
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
    if not certificate:
        return Response({"certificate_validity": VerificationResult.NOT_FOUND, "certificate_number": certificate_number}, status=404)
    payload = CertificatePublicVerificationSerializer(certificate).data
    payload["certificate_validity"] = result
    return Response(payload)
