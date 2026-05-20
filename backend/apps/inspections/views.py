from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.inspections.models import Inspection
from apps.inspections.serializers import (
    CertificateScanSerializer,
    CreateInspectionSerializer,
    InspectionCertificateScanSerializer,
    InspectionEvidenceSerializer,
    InspectionSerializer,
)
from apps.inspections.services import InspectionService


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
