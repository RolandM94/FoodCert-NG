from django.conf import settings
from django.http import FileResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.locations.models import LGA, State
from apps.reports.models import (
    DashboardWidget,
    DataQualityIssue,
    GeneratedReport,
    GeneratedReportStatus,
    MEIndicator,
    ReportSchedule,
    ReportTemplate,
    ReportType,
    ScheduledReport,
)
from apps.reports.serializers import (
    AnalyticsQuerySerializer,
    DashboardQuerySerializer,
    DashboardWidgetSerializer,
    DataQualityIssueSerializer,
    GenerateReportSerializer,
    GeneratedReportSerializer,
    MECalculationSerializer,
    MEIndicatorSerializer,
    MEIndicatorValueSerializer,
    ReportScheduleSerializer,
    ScheduledReportSerializer,
    ReportTemplateSerializer,
    ReportReviewActionSerializer,
)
from apps.reports.services import AnalyticsService, DashboardService, MEIndicatorService, ReportService


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


class FoodHandlerDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(DashboardService.food_handler_dashboard(request.user))


class DoctorDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(parameters=[DashboardQuerySerializer], responses=dict)
    def get(self, request):
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(DashboardService.doctor_dashboard(request.user, facility_id=serializer.validated_data.get("facility")))


class LabDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(parameters=[DashboardQuerySerializer], responses=dict)
    def get(self, request):
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(DashboardService.lab_dashboard(request.user, facility_id=serializer.validated_data.get("facility")))


class InspectorDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(DashboardService.inspector_dashboard(request.user))


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(DashboardService.admin_dashboard(request.user))


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
                date_from=serializer.validated_data.get("date_from"),
                date_to=serializer.validated_data.get("date_to"),
                doctor_id=serializer.validated_data.get("doctor"),
                lab_status=serializer.validated_data.get("lab_status", ""),
                assessment_status=serializer.validated_data.get("assessment_status", ""),
                employer_category=serializer.validated_data.get("employer_category", ""),
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


class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    service_method = None
    finance_only = False

    @extend_schema(parameters=[AnalyticsQuerySerializer], responses=dict)
    def get(self, request):
        if self.finance_only and request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("Finance analytics require finance oversight permissions.")
        if not self.finance_only and request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            raise PermissionDenied("You cannot access analytics.")
        serializer = AnalyticsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        filters = AnalyticsService.filters_from_request(serializer.validated_data, request.user)
        return Response(self.service_method(filters))


class CertificateAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.certificate_analytics


class AssessmentAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.assessment_analytics


class VaccinationAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.vaccination_analytics


class FacilityAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.facility_analytics


class EmployerAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.employer_analytics


class InspectionAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.inspection_analytics


class EnforcementAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.enforcement_analytics


class IllnessAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.illness_analytics


class PaymentAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.payment_analytics
    finance_only = True


class SettlementAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.settlement_analytics
    finance_only = True


class DataQualityAnalyticsView(AnalyticsView):
    service_method = AnalyticsService.data_quality_analytics


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


class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.select_related("created_by").order_by("scope", "name")
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["scope", "module", "privacy_level", "is_active"]
    search_fields = ["code", "name", "description", "module"]

    ROLE_SCOPES = {
        UserRole.FOOD_HANDLER: {"food_handler"},
        UserRole.EMPLOYER: {"employer"},
        UserRole.FACILITY_ADMIN: {"facility"},
        UserRole.DOCTOR: {"facility", "doctor"},
        UserRole.LAB_STAFF: {"facility", "lab"},
        UserRole.INSPECTOR: {"inspector"},
        UserRole.STATE_ADMIN: {"state"},
        UserRole.FEDERAL_ADMIN: {"federal"},
        UserRole.SUPER_ADMIN: {"admin", "federal", "state", "facility", "doctor", "lab", "inspector", "employer", "food_handler"},
    }

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return self.queryset
        scopes = self.ROLE_SCOPES.get(user.role, set())
        return self.queryset.filter(is_active=True, scope__in=scopes)

    def _ensure_super_admin(self):
        if self.request.user.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Only super admins can manage report templates.")

    def perform_create(self, serializer):
        self._ensure_super_admin()
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        self._ensure_super_admin()
        serializer.save()

    def perform_destroy(self, instance):
        self._ensure_super_admin()
        instance.delete()


class MEIndicatorViewSet(viewsets.ModelViewSet):
    queryset = MEIndicator.objects.order_by("category", "name")
    serializer_class = MEIndicatorSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["category", "reporting_frequency", "is_active"]
    search_fields = ["code", "name", "description", "category"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        if self.request.user.role == UserRole.SUPER_ADMIN:
            return self.queryset
        return self.queryset.filter(is_active=True)

    def _ensure_super_admin(self):
        if self.request.user.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Only super admins can manage M&E indicators.")

    def perform_create(self, serializer):
        self._ensure_super_admin()
        serializer.save()

    def perform_update(self, serializer):
        self._ensure_super_admin()
        serializer.save()

    @extend_schema(responses=MEIndicatorValueSerializer(many=True))
    @action(detail=True, methods=["get"], url_path="values")
    def values(self, request, pk=None):
        periods = int(request.query_params.get("periods", 12))
        return Response(MEIndicatorValueSerializer(MEIndicatorService.get_indicator_history(self.get_object().id, periods=periods), many=True).data)


class MECalculateView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=MECalculationSerializer, responses=MEIndicatorValueSerializer(many=True))
    def post(self, request):
        serializer = MECalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        state = State.objects.filter(id=serializer.validated_data.get("state")).first() if serializer.validated_data.get("state") else None
        lga = LGA.objects.filter(id=serializer.validated_data.get("lga")).first() if serializer.validated_data.get("lga") else None
        period_start = serializer.validated_data.get("period_start")
        period_end = serializer.validated_data.get("period_end")
        if serializer.validated_data.get("indicator"):
            indicator = MEIndicator.objects.get(id=serializer.validated_data["indicator"])
            values = [MEIndicatorService.calculate_indicator(indicator, state=state, lga=lga, period_start=period_start, period_end=period_end)]
        elif serializer.validated_data.get("category"):
            values = MEIndicatorService.calculate_category(serializer.validated_data["category"], state=state, period_start=period_start, period_end=period_end)
        else:
            values = MEIndicatorService.calculate_all_indicators(state=state, period_start=period_start, period_end=period_end)
        return Response(MEIndicatorValueSerializer(values, many=True).data, status=status.HTTP_201_CREATED)


class MEDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=dict)
    def get(self, request):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("You cannot access the M&E dashboard.")
        if request.user.role == UserRole.STATE_ADMIN and request.user.state_id:
            return Response(MEIndicatorService.get_state_performance(request.user.state_id))
        return Response(MEIndicatorService.get_national_summary())


class MEStatePerformanceView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(parameters=[DashboardQuerySerializer], responses=dict)
    def get(self, request):
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        state_id = serializer.validated_data.get("state") or getattr(request.user, "state_id", None)
        if not state_id:
            raise PermissionDenied("A state is required for state performance.")
        if request.user.role == UserRole.STATE_ADMIN and str(request.user.state_id) != str(state_id):
            raise PermissionDenied("State users can only access their own state performance.")
        return Response(MEIndicatorService.get_state_performance(state_id))


class MENationalSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=dict)
    def get(self, request):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only federal and super admin users can access national M&E summaries.")
        return Response(MEIndicatorService.get_national_summary())


class GeneratedReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GeneratedReport.objects.select_related("generated_by", "schedule", "organization", "state", "reviewed_by").order_by("-created_at")
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

    @extend_schema(responses=GeneratedReportSerializer)
    @action(detail=True, methods=["post"], url_path="submit-to-federal")
    def submit_to_federal(self, request, pk=None):
        return Response(GeneratedReportSerializer(ReportService.submit_to_federal(report=self.get_object(), actor=request.user)).data)

    @extend_schema(responses=GeneratedReportSerializer)
    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        return Response(GeneratedReportSerializer(ReportService.archive(report=self.get_object(), actor=request.user)).data)

    @extend_schema(responses={201: GeneratedReportSerializer})
    @action(detail=True, methods=["post"], url_path="regenerate")
    def regenerate(self, request, pk=None):
        return Response(GeneratedReportSerializer(ReportService.regenerate(report=self.get_object(), actor=request.user)).data, status=status.HTTP_201_CREATED)


class FederalStateReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GeneratedReport.objects.select_related("generated_by", "organization", "state", "reviewed_by").filter(
        state__isnull=False,
        status__in=[
            GeneratedReportStatus.SUBMITTED,
            GeneratedReportStatus.ACCEPTED,
            GeneratedReportStatus.RETURNED_FOR_CORRECTION,
        ],
    ).order_by("-submitted_to_federal_at", "-created_at")
    serializer_class = GeneratedReportSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["report_type", "status", "state"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        if self.request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only federal users can access submitted state reports.")
        return self.queryset

    @extend_schema(request=ReportReviewActionSerializer, responses=GeneratedReportSerializer)
    @action(detail=True, methods=["post"], url_path="accept")
    def accept(self, request, pk=None):
        serializer = ReportReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = ReportService.accept_federal_report(report=self.get_object(), actor=request.user, comment=serializer.validated_data.get("comment", ""))
        return Response(GeneratedReportSerializer(report).data)

    @extend_schema(request=ReportReviewActionSerializer, responses=GeneratedReportSerializer)
    @action(detail=True, methods=["post"], url_path="return-for-correction")
    def return_for_correction(self, request, pk=None):
        serializer = ReportReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = ReportService.return_for_correction(report=self.get_object(), actor=request.user, comment=serializer.validated_data.get("comment", ""))
        return Response(GeneratedReportSerializer(report).data)

    @extend_schema(request=ReportReviewActionSerializer, responses=GeneratedReportSerializer)
    @action(detail=True, methods=["post"], url_path="escalate")
    def escalate(self, request, pk=None):
        serializer = ReportReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = ReportService.escalate_federal_report(report=self.get_object(), actor=request.user, comment=serializer.validated_data.get("comment", ""))
        return Response(GeneratedReportSerializer(report).data)


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    queryset = DashboardWidget.objects.order_by("dashboard_scope", "sort_order", "name")
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["dashboard_scope", "widget_type", "is_active"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        scope = self.request.query_params.get("dashboard_scope")
        qs = self.queryset
        if scope:
            qs = qs.filter(dashboard_scope=scope)
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return qs
        role_scopes = {
            UserRole.FOOD_HANDLER: ["food_handler"],
            UserRole.EMPLOYER: ["employer"],
            UserRole.FACILITY_ADMIN: ["facility"],
            UserRole.DOCTOR: ["doctor"],
            UserRole.LAB_STAFF: ["lab"],
            UserRole.INSPECTOR: ["inspector"],
            UserRole.STATE_ADMIN: ["state"],
            UserRole.FEDERAL_ADMIN: ["federal"],
        }
        allowed = set(role_scopes.get(user.role, []))
        return qs.filter(is_active=True, dashboard_scope__in=allowed)

    def _ensure_admin(self):
        if self.request.user.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Only super admins can manage dashboard widgets.")

    def perform_create(self, serializer):
        self._ensure_admin()
        serializer.save()

    def perform_update(self, serializer):
        self._ensure_admin()
        serializer.save()

    def perform_destroy(self, instance):
        self._ensure_admin()
        instance.delete()


class DataQualityIssueViewSet(viewsets.ModelViewSet):
    queryset = DataQualityIssue.objects.select_related("state", "organization", "assigned_to", "resolved_by").order_by("-created_at")
    serializer_class = DataQualityIssueSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "patch", "head", "options"]
    filterset_fields = ["issue_type", "severity", "module", "status", "state"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return self.queryset
        if user.role == UserRole.FEDERAL_ADMIN:
            return self.queryset
        if user.role == UserRole.STATE_ADMIN and user.state_id:
            return self.queryset.filter(state_id=user.state_id)
        if user.role == UserRole.EMPLOYER and user.organization_id:
            return self.queryset.filter(organization_id=user.organization_id)
        return self.queryset.none()

    @extend_schema(request=ReportReviewActionSerializer, responses=DataQualityIssueSerializer)
    @action(detail=True, methods=["post"], url_path="assign")
    def assign(self, request, pk=None):
        issue = self.get_object()
        serializer = ReportReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignee_id = serializer.validated_data.get("comment")
        if assignee_id:
            from apps.accounts.models import User
            assignee = User.objects.filter(id=assignee_id).first()
            if assignee:
                issue.assigned_to = assignee
                issue.status = "assigned"
                issue.save(update_fields=["assigned_to", "status", "updated_at"])
        return Response(DataQualityIssueSerializer(issue).data)

    @extend_schema(responses=DataQualityIssueSerializer)
    @action(detail=True, methods=["post"], url_path="resolve")
    def resolve(self, request, pk=None):
        issue = self.get_object()
        issue.status = "resolved"
        issue.resolved_by = request.user
        issue.resolved_at = timezone.now()
        issue.save(update_fields=["status", "resolved_by", "resolved_at", "updated_at"])
        return Response(DataQualityIssueSerializer(issue).data)

    @extend_schema(responses=DataQualityIssueSerializer)
    @action(detail=True, methods=["post"], url_path="escalate")
    def escalate(self, request, pk=None):
        issue = self.get_object()
        issue.status = "escalated"
        issue.save(update_fields=["status", "updated_at"])
        return Response(DataQualityIssueSerializer(issue).data)


class ScheduledReportViewSet(viewsets.ModelViewSet):
    queryset = ScheduledReport.objects.select_related("report_template", "owner").order_by("-created_at")
    serializer_class = ScheduledReportSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ["schedule_frequency", "is_active"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        return self.queryset.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(responses={201: GeneratedReportSerializer})
    @action(detail=True, methods=["post"], url_path="run-now")
    def run_now(self, request, pk=None):
        scheduled = self.get_object()
        report = ReportService.generate(
            report_type=ReportType.STATE_MONTHLY,
            user=request.user,
            file_format=scheduled.output_format or "json",
            filters=scheduled.filters or {},
        )
        scheduled.last_run_at = timezone.now()
        next_map = {"daily": 1, "weekly": 7, "monthly": 30, "quarterly": 90}
        days = next_map.get(scheduled.schedule_frequency, 30)
        scheduled.next_run_at = timezone.now() + timezone.timedelta(days=days)
        scheduled.save(update_fields=["last_run_at", "next_run_at", "updated_at"])
        return Response(GeneratedReportSerializer(report).data, status=status.HTTP_201_CREATED)
