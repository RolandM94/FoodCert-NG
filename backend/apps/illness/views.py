from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.illness.models import IllnessReport
from apps.illness.serializers import (
    CreateIllnessReportSerializer,
    IllnessClearanceSerializer,
    IllnessReportSerializer,
    ReviewIllnessReportSerializer,
)
from apps.illness.services import IllnessService


class IllnessReportViewSet(viewsets.ModelViewSet):
    queryset = IllnessReport.objects.select_related(
        "food_handler",
        "food_handler__user",
        "employer",
        "reported_by",
        "reviewed_by_doctor",
    ).order_by("-created_at")
    serializer_class = IllnessReportSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["clearance_status", "suspected_condition", "food_handler", "employer"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR, UserRole.DOCTOR}:
            return self.queryset.filter(food_handler__state=user.state)
        if user.role == UserRole.FOOD_HANDLER:
            return self.queryset.filter(food_handler__user=user)
        if user.role == UserRole.EMPLOYER and hasattr(user, "employer"):
            return self.queryset.filter(employer=user.employer)
        return self.queryset.none()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateIllnessReportSerializer
        return IllnessReportSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateIllnessReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = IllnessService.report(
            food_handler=serializer.validated_data["food_handler"],
            reported_by=request.user,
            symptoms=serializer.validated_data.get("symptoms", {}),
            suspected_condition=serializer.validated_data.get("suspected_condition", ""),
            symptom_start_date=serializer.validated_data.get("symptom_start_date"),
            symptom_end_date=serializer.validated_data.get("symptom_end_date"),
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(IllnessReportSerializer(report).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=ReviewIllnessReportSerializer, responses=IllnessReportSerializer)
    @action(detail=True, methods=["patch"], url_path="review")
    def review(self, request, pk=None):
        serializer = ReviewIllnessReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = IllnessService.review(
            report=self.get_object(),
            doctor=request.user,
            notes=serializer.validated_data.get("notes", ""),
            symptom_end_date=serializer.validated_data.get("symptom_end_date"),
            suspected_condition=serializer.validated_data.get("suspected_condition"),
        )
        return Response(IllnessReportSerializer(report).data)

    @extend_schema(request=IllnessClearanceSerializer, responses=IllnessReportSerializer)
    @action(detail=True, methods=["patch"], url_path="clearance")
    def clearance(self, request, pk=None):
        serializer = IllnessClearanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = IllnessService.clearance(
            report=self.get_object(),
            doctor=request.user,
            cleared=serializer.validated_data["cleared"],
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(IllnessReportSerializer(report).data)
