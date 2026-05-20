from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.lab_tests.models import LabTest
from apps.lab_tests.serializers import LabTestResultSerializer, LabTestSerializer
from apps.lab_tests.services import LabTestService


class LabTestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LabTest.objects.select_related(
        "assessment",
        "assessment__food_handler",
        "assessment__facility",
        "assessment__facility__organization",
        "requested_by",
        "resulted_by",
        "reviewed_by",
    ).order_by("-created_at")
    serializer_class = LabTestSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["status", "test_type", "assessment"]
    ordering_fields = ["created_at", "requested_at", "resulted_at", "reviewed_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
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
        )
        return Response(LabTestSerializer(lab_test).data)

    @extend_schema(responses=LabTestSerializer)
    @action(detail=True, methods=["patch"], url_path="review")
    def review(self, request, pk=None):
        lab_test = self.get_object()
        lab_test = LabTestService.review(lab_test=lab_test, doctor=request.user)
        return Response(LabTestSerializer(lab_test).data)
