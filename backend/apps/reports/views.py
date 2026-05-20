from django.conf import settings
from django.http import FileResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.reports.models import GeneratedReport, ReportSchedule, ReportType
from apps.reports.serializers import (
    DashboardQuerySerializer,
    GenerateReportSerializer,
    GeneratedReportSerializer,
    ReportScheduleSerializer,
)
from apps.reports.services import DashboardService, ReportService


class EmployerDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(parameters=[DashboardQuerySerializer], responses=dict)
    def get(self, request):
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(
            DashboardService.employer_dashboard(
                request.user,
                employer_id=serializer.validated_data.get("employer"),
                branch_id=serializer.validated_data.get("branch"),
            )
        )


class FacilityDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(parameters=[DashboardQuerySerializer], responses=dict)
    def get(self, request):
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(
            DashboardService.facility_dashboard(
                request.user,
                facility_id=serializer.validated_data.get("facility"),
                department_id=serializer.validated_data.get("department"),
            )
        )


class StateDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(parameters=[DashboardQuerySerializer], responses=dict)
    def get(self, request):
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(
            DashboardService.state_dashboard(
                request.user,
                state_id=serializer.validated_data.get("state"),
                lga_id=serializer.validated_data.get("lga"),
                date_from=serializer.validated_data.get("date_from"),
                date_to=serializer.validated_data.get("date_to"),
                employer_category=serializer.validated_data.get("employer_category", ""),
                certificate_status=serializer.validated_data.get("certificate_status", ""),
            )
        )


class FederalDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(DashboardService.federal_dashboard(request.user))


class ReportGenerateView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    report_type = None

    @extend_schema(request=GenerateReportSerializer, responses={201: GeneratedReportSerializer})
    def get(self, request):
        serializer = GenerateReportSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        report = ReportService.generate(
            report_type=self.report_type,
            user=request.user,
            file_format=serializer.validated_data.get("file_format", "json"),
            filters=serializer.validated_data.get("filters", {}),
        )
        return Response(GeneratedReportSerializer(report).data)


class EmployerComplianceReportView(ReportGenerateView):
    report_type = ReportType.EMPLOYER_COMPLIANCE


class FacilityPerformanceReportView(ReportGenerateView):
    report_type = ReportType.FACILITY_PERFORMANCE


class StateMonthlyReportView(ReportGenerateView):
    report_type = ReportType.STATE_MONTHLY


class NationalReportView(ReportGenerateView):
    report_type = ReportType.NATIONAL


class VaccinationCoverageReportView(ReportGenerateView):
    report_type = ReportType.VACCINATION_COVERAGE


class IllnessTrendsReportView(ReportGenerateView):
    report_type = ReportType.ILLNESS_TRENDS


class InspectionOutcomesReportView(ReportGenerateView):
    report_type = ReportType.INSPECTION_OUTCOMES


class ReportScheduleViewSet(viewsets.ModelViewSet):
    queryset = ReportSchedule.objects.select_related("created_by").order_by("-created_at")
    serializer_class = ReportScheduleSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["report_type", "status", "frequency"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        return self.queryset.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class GeneratedReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GeneratedReport.objects.select_related("generated_by", "schedule").order_by("-created_at")
    serializer_class = GeneratedReportSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["report_type", "file_format", "status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        return self.queryset.filter(generated_by=user)

    @extend_schema(responses=GeneratedReportSerializer)
    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        report = self.get_object()
        if not report.file_url:
            raise NotFound("Report file is not available.")
        relative_path = report.file_url.replace("http://localhost:8000/media/", "")
        file_path = settings.MEDIA_ROOT / relative_path
        if not file_path.exists():
            raise NotFound("Report file was not found.")
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=file_path.name)
