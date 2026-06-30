from drf_spectacular.utils import extend_schema
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.lab_tests.models import LabTest
from apps.lab_tests.serializers import LabDoctorReviewSerializer, LabResultUploadSerializer, LabSampleCollectedSerializer, LabSubmitToDoctorSerializer, LabTestRepeatRequestSerializer, LabTestResultSerializer, LabTestSerializer
from apps.lab_tests.services import LabTestService


class LabTestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LabTest.objects.select_related(
        "assessment",
        "assessment__food_handler",
        "assessment__facility",
        "assessment__facility__organization",
        "assigned_lab_staff",
        "assigned_lab_unit",
        "requested_by",
        "resulted_by",
        "reviewed_by",
    ).order_by("-created_at")
    serializer_class = LabTestSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filterset_fields = ["status", "test_type", "assessment"]
    ordering_fields = ["created_at", "requested_at", "resulted_at", "reviewed_at"]

    def retrieve(self, request, *args, **kwargs):
        lab_test = self.get_object()
        if request.user.role in {UserRole.FACILITY_ADMIN, UserRole.DOCTOR, UserRole.LAB_STAFF}:
            log_action(
                action=AuditAction.MEDICAL_RECORD_ACCESS,
                actor=request.user,
                target=lab_test,
                request=request,
                metadata={"event": "lab_result_read", "assessment_id": str(lab_test.assessment_id)},
            )
        serializer = self.get_serializer(lab_test)
        return Response(serializer.data)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return self.queryset
        if user.role == UserRole.FEDERAL_ADMIN:
            return self.queryset.none()
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return self.queryset.filter(assessment__facility__state=user.state)
        if user.role == UserRole.FOOD_HANDLER:
            return self.queryset.none()
        if user.role == UserRole.EMPLOYER:
            return self.queryset.none()
        if user.organization_id:
            return self.queryset.filter(assessment__facility__organization=user.organization)
        return self.queryset.none()

    @extend_schema(request=LabTestResultSerializer, responses=LabTestSerializer)
    @action(detail=True, methods=["patch"], url_path="result")
    def result(self, request, pk=None):
        lab_test = self.get_object()
        serializer = LabTestResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lab_test = LabTestService.record_result(
            lab_test=lab_test,
            actor=request.user,
            status=serializer.validated_data["status"],
            result_value=serializer.validated_data.get("result_value", ""),
            result_notes=serializer.validated_data.get("result_notes", ""),
            lab_staff_notes=serializer.validated_data.get("lab_staff_notes", ""),
        )
        return Response(LabTestSerializer(lab_test).data)

    @extend_schema(request=LabSampleCollectedSerializer, responses=LabTestSerializer)
    @action(detail=True, methods=["patch"], url_path="sample-collected")
    def sample_collected(self, request, pk=None):
        lab_test = self.get_object()
        serializer = LabSampleCollectedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lab_test = LabTestService.mark_sample_collected(
            lab_test=lab_test,
            actor=request.user,
            lab_staff_notes=serializer.validated_data.get("lab_staff_notes", ""),
        )
        return Response(LabTestSerializer(lab_test).data)

    @extend_schema(request=LabResultUploadSerializer, responses=LabTestSerializer)
    @action(detail=True, methods=["post"], url_path="upload-result")
    def upload_result(self, request, pk=None):
        lab_test = self.get_object()
        serializer = LabResultUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lab_test = LabTestService.upload_result_document(
            lab_test=lab_test,
            actor=request.user,
            result_document=serializer.validated_data["result_document"],
            lab_staff_notes=serializer.validated_data.get("lab_staff_notes", ""),
        )
        return Response(LabTestSerializer(lab_test).data)

    @extend_schema(request=LabSubmitToDoctorSerializer, responses=LabTestSerializer)
    @action(detail=True, methods=["patch"], url_path="submit-to-doctor")
    def submit_to_doctor(self, request, pk=None):
        lab_test = self.get_object()
        serializer = LabSubmitToDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lab_test = LabTestService.submit_to_doctor(
            lab_test=lab_test,
            actor=request.user,
            lab_staff_notes=serializer.validated_data.get("lab_staff_notes", ""),
        )
        return Response(LabTestSerializer(lab_test).data)

    @extend_schema(request=LabDoctorReviewSerializer, responses=LabTestSerializer)
    @action(detail=True, methods=["post", "patch"], url_path="review")
    def review(self, request, pk=None):
        lab_test = self.get_object()
        serializer = LabDoctorReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lab_test = LabTestService.review(
            lab_test=lab_test,
            doctor=request.user,
            doctor_review_notes=serializer.validated_data.get("doctor_review_notes", ""),
            doctor_recommendation=serializer.validated_data.get("doctor_recommendation", ""),
        )
        return Response(LabTestSerializer(lab_test).data)

    @extend_schema(request=LabTestRepeatRequestSerializer, responses=LabTestSerializer)
    @action(detail=True, methods=["post"], url_path="request-repeat")
    def request_repeat(self, request, pk=None):
        lab_test = self.get_object()
        serializer = LabTestRepeatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        repeat = LabTestService.request_repeat(
            lab_test=lab_test,
            doctor=request.user,
            reason=serializer.validated_data["reason"],
            test_name=serializer.validated_data.get("test_name", ""),
        )
        return Response(LabTestSerializer(repeat).data)


class LabRequestViewSet(LabTestViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == UserRole.LAB_STAFF:
            filters = Q(assigned_lab_staff=user)
            if getattr(user, "unit_id", None):
                filters |= Q(assigned_lab_unit_id=user.unit_id, assigned_lab_staff__isnull=True)
            return queryset.filter(filters)
        if user.role == UserRole.DOCTOR:
            return queryset.filter(assessment__doctor=user)
        return queryset
