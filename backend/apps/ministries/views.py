import csv

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserInvite, UserRole
from apps.accounts.permissions import IsActiveUser
from apps.accounts.services import InviteService
from apps.audit.models import AuditAction, AuditLog
from apps.audit.services import log_action
from apps.certificates.models import AccreditationCertificate, AccreditationCertificateType, Certificate, CertificateRequest, CertificateRequestStatus, CertificateStatus, CertificateVerificationLog, SuspiciousCertificateReport, VerificationResult
from apps.certificates.services import CertificateService
from apps.facilities.models import AccreditationStatus, FacilityAccreditationApplication, MedicalFacility
from apps.facilities.serializers import FacilityAccreditationApplicationSerializer, MedicalFacilitySerializer
from apps.facilities.services import FacilityAccreditationService
from apps.ministries.permissions import IsFederalMinistryUser, IsStateMinistryUser, can_manage_state_users
from apps.ministries.permissions import can_assign_inspections, can_manage_federal_queries, can_manage_national_policy, can_manage_state_fees, can_review_facility_accreditation, can_submit_state_reports, can_validate_certificates
from apps.ministries.serializers import (
    DashboardQuerySerializer,
    OrganizationUnitSerializer,
    StateCertificateValidationActionSerializer,
    StateCertificateValidationSerializer,
    StateCertificateLifecycleActionSerializer,
    StateCertificateRegistrySerializer,
    StateEmployerMonitoringSerializer,
    StateFoodHandlerMonitoringSerializer,
    StateIllnessMonitoringSerializer,
    StateInspectionAssignmentSerializer,
    StateInspectionCloseSerializer,
    StateInspectionReviewSerializer,
    StateInspectionSerializer,
    StateMinistryInviteCreateSerializer,
    StateMinistryInviteSerializer,
    StateMinistryUserSerializer,
    StateReportGenerateSerializer,
    StateReportSerializer,
    FederalCertificateRegistrySerializer,
    FederalEmployerRegistrySerializer,
    FederalFacilityRegistrySerializer,
    NationalPolicyConfigSerializer,
    StatePolicyConfigSerializer,
    FederalStateQueryCreateSerializer,
    FederalStateQueryResponseSerializer,
    FederalStateQuerySerializer,
)
from apps.ministries.models import FederalStateQuery, StateReport
from apps.ministries.services import FederalFinanceService, FederalOversightService, FederalPerformanceService, MinistryDashboardService, StateReportService, get_state_ministry_organization
from apps.organizations.models import OrganizationUnit
from apps.organizations.services import create_unit, deactivate_unit, update_unit
from apps.payments.models import ActiveStatus, AssessmentFee, PaymentTransaction, RefundRequest
from apps.payments.serializers import AssessmentFeeSerializer, RefundRequestSerializer
from apps.employers.models import ComplianceStatus, Employer
from apps.food_handlers.models import FoodHandlerProfile
from apps.illness.models import IllnessReport
from apps.inspections.models import Inspection, InspectionStatus
from apps.inspections.services import InspectionService
from apps.settlements.models import Settlement
from apps.settlements.serializers import SettlementSerializer
from apps.policy.models import NationalPolicyConfig, StatePolicyConfig


User = get_user_model()


class StateDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(parameters=[DashboardQuerySerializer], responses=dict)
    def get(self, request):
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(
            MinistryDashboardService.state_dashboard(
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
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(MinistryDashboardService.federal_dashboard(request.user))


class FederalStatePerformanceView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(FederalPerformanceService.state_performance())


class FederalStateSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=dict)
    def get(self, request, state_id):
        return Response(FederalPerformanceService.state_summary(state_id))


class FederalFinanceDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(
            FederalFinanceService.dashboard(
                date_from=request.query_params.get("date_from"),
                date_to=request.query_params.get("date_to"),
            )
        )


class FederalFinanceRevenueByStateView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(
            FederalFinanceService.revenue_by_state(
                date_from=request.query_params.get("date_from"),
                date_to=request.query_params.get("date_to"),
            )
        )


class FederalFinanceSubscriptionsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(FederalFinanceService.subscription_summary())


class FederalFinanceSettlementListView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=SettlementSerializer(many=True))
    def get(self, request):
        queryset = Settlement.objects.select_related("facility", "state", "payment_transaction").order_by("-created_at")
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(settlement_status=status_filter)
        state = request.query_params.get("state")
        if state:
            queryset = queryset.filter(state_id=state)
        return Response(SettlementSerializer(queryset[:500], many=True).data)


class FederalCertificateRegistryView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=FederalCertificateRegistrySerializer(many=True))
    def get(self, request):
        queryset = (
            Certificate.objects.select_related("food_handler", "employer", "facility", "issuing_state")
            .annotate(suspicious_report_count=Count("suspicious_reports", distinct=True))
            .order_by("-issue_date", "-created_at")
        )
        state = request.query_params.get("state")
        if state:
            queryset = queryset.filter(issuing_state_id=state)
        status_filter = request.query_params.get("status")
        if status_filter:
            if status_filter == CertificateStatus.EXPIRED:
                queryset = queryset.filter(status=CertificateStatus.ACTIVE, expiry_date__lt=timezone.localdate())
            else:
                queryset = queryset.filter(status=status_filter)
        facility = request.query_params.get("facility")
        if facility:
            queryset = queryset.filter(facility_id=facility)
        employer = request.query_params.get("employer")
        if employer:
            queryset = queryset.filter(employer_id=employer)
        issue_from = request.query_params.get("issue_from") or request.query_params.get("date_from")
        if issue_from:
            queryset = queryset.filter(issue_date__gte=issue_from)
        issue_to = request.query_params.get("issue_to") or request.query_params.get("date_to")
        if issue_to:
            queryset = queryset.filter(issue_date__lte=issue_to)
        expiry_from = request.query_params.get("expiry_from")
        if expiry_from:
            queryset = queryset.filter(expiry_date__gte=expiry_from)
        expiry_to = request.query_params.get("expiry_to")
        if expiry_to:
            queryset = queryset.filter(expiry_date__lte=expiry_to)
        flagged_filter = request.query_params.get("flagged") or request.query_params.get("suspicious")
        if flagged_filter == "true":
            queryset = queryset.filter(suspicious_reports__isnull=False).distinct()
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(certificate_number__icontains=search)
                | Q(food_handler__full_name__icontains=search)
                | Q(employer__business_name__icontains=search)
                | Q(facility__facility_name__icontains=search)
            )
        return Response(FederalCertificateRegistrySerializer(queryset[:500], many=True).data)


class FederalCertificateDetailView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=FederalCertificateRegistrySerializer)
    def get(self, request, pk):
        certificate = get_object_or_404(
            Certificate.objects.select_related("food_handler", "employer", "facility", "issuing_state").annotate(
                suspicious_report_count=Count("suspicious_reports", distinct=True),
            ),
            pk=pk,
        )
        log_action(
            action=AuditAction.CERTIFICATE_EVENT,
            actor=request.user,
            target=certificate,
            metadata={"event": "federal_certificate_detail_viewed"},
        )
        return Response(FederalCertificateRegistrySerializer(certificate).data)


class FederalCertificateAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=dict)
    def get(self, request):
        today = timezone.localdate()
        thirty_days = today + timezone.timedelta(days=30)
        certificates = Certificate.objects.all()
        by_state = list(
            certificates.values("issuing_state__name")
            .annotate(
                total=Count("id"),
                active=Count("id", filter=Q(status=CertificateStatus.ACTIVE, expiry_date__gte=today)),
                expired=Count("id", filter=Q(expiry_date__lt=today) | Q(status=CertificateStatus.EXPIRED)),
                suspended=Count("id", filter=Q(status=CertificateStatus.SUSPENDED)),
                revoked=Count("id", filter=Q(status=CertificateStatus.REVOKED)),
            )
            .order_by("issuing_state__name")
        )
        status_distribution = list(certificates.values("status").annotate(total=Count("id")).order_by("status"))
        high_risk_facilities = list(
            certificates.values("facility__id", "facility__facility_name", "issuing_state__name")
            .annotate(
                total=Count("id"),
                suspended=Count("id", filter=Q(status=CertificateStatus.SUSPENDED)),
                revoked=Count("id", filter=Q(status=CertificateStatus.REVOKED)),
                flagged=Count("suspicious_reports", distinct=True),
            )
            .filter(Q(suspended__gt=0) | Q(revoked__gt=0) | Q(flagged__gt=0))
            .order_by("-flagged", "-revoked", "-suspended", "facility__facility_name")[:10]
        )
        invalid_trends = list(
            CertificateVerificationLog.objects.filter(result__in=[VerificationResult.INVALID, VerificationResult.NOT_FOUND])
            .extra(select={"day": "date(created_at)"})
            .values("day")
            .annotate(total=Count("id"))
            .order_by("-day")[:14]
        )
        invalid_attempts = CertificateVerificationLog.objects.filter(result__in=[VerificationResult.INVALID, VerificationResult.NOT_FOUND]).count()
        flagged_count = SuspiciousCertificateReport.objects.count()
        return Response({
            "cards": {
                "total": certificates.count(),
                "active": certificates.filter(status=CertificateStatus.ACTIVE, expiry_date__gte=today).count(),
                "expired": certificates.filter(Q(status=CertificateStatus.EXPIRED) | Q(expiry_date__lt=today)).count(),
                "expiring_30_days": certificates.filter(status=CertificateStatus.ACTIVE, expiry_date__gte=today, expiry_date__lte=thirty_days).count(),
                "suspended": certificates.filter(status=CertificateStatus.SUSPENDED).count(),
                "revoked": certificates.filter(status=CertificateStatus.REVOKED).count(),
                "flagged": flagged_count,
                "invalid_verification_attempts": invalid_attempts,
            },
            "by_state": [
                {
                    "state_name": row["issuing_state__name"] or "Unknown",
                    "total": row["total"],
                    "active": row["active"],
                    "expired": row["expired"],
                    "suspended": row["suspended"],
                    "revoked": row["revoked"],
                }
                for row in by_state
            ],
            "status_distribution": [{"status": row["status"], "total": row["total"]} for row in status_distribution],
            "invalid_verification_trends": [{"day": str(row["day"]), "total": row["total"]} for row in invalid_trends],
            "high_risk_facilities": [
                {
                    "facility_id": str(row["facility__id"]) if row["facility__id"] else None,
                    "facility_name": row["facility__facility_name"] or "Unknown facility",
                    "state_name": row["issuing_state__name"] or "Unknown",
                    "total": row["total"],
                    "suspended": row["suspended"],
                    "revoked": row["revoked"],
                    "flagged": row["flagged"],
                }
                for row in high_risk_facilities
            ],
        })


class FederalCertificateFlagView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    def post(self, request, pk):
        certificate = get_object_or_404(Certificate, pk=pk)
        reason = request.data.get("reason", "").strip()
        if not reason:
            raise ValidationError("Reason is required.")
        report = SuspiciousCertificateReport.objects.create(
            certificate=certificate,
            certificate_number_submitted=certificate.certificate_number,
            verification_token_submitted=certificate.verification_token or "",
            reporter_name=request.user.get_full_name() or request.user.email,
            reporter_contact=request.user.email,
            reason=reason,
            details=request.data.get("details", ""),
        )
        log_action(
            action=AuditAction.CERTIFICATE_EVENT,
            actor=request.user,
            target=certificate,
            metadata={"event": "federal_certificate_flagged", "report_id": str(report.id), "reason": reason},
        )
        return Response({"status": "flagged", "report_id": str(report.id)}, status=status.HTTP_201_CREATED)


class FederalFacilityRegistryView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=FederalFacilityRegistrySerializer(many=True))
    def get(self, request):
        queryset = MedicalFacility.objects.select_related("state", "lga").order_by("state__name", "facility_name")
        state = request.query_params.get("state")
        if state:
            queryset = queryset.filter(state_id=state)
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(accreditation_status=status_filter)
        facility_type = request.query_params.get("facility_type")
        if facility_type:
            queryset = queryset.filter(facility_type=facility_type)
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(facility_name__icontains=search) | Q(license_number__icontains=search))
        return Response(FederalFacilityRegistrySerializer(queryset[:500], many=True).data)


class FederalEmployerRegistryView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=FederalEmployerRegistrySerializer(many=True))
    def get(self, request):
        queryset = Employer.objects.select_related("state", "lga").annotate(food_handler_count=Count("food_handlers")).order_by("state__name", "business_name")
        state = request.query_params.get("state")
        if state:
            queryset = queryset.filter(state_id=state)
        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(establishment_category=category)
        compliance_status = request.query_params.get("compliance_status")
        if compliance_status:
            queryset = queryset.filter(compliance_status=compliance_status)
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(business_name__icontains=search) | Q(business_registration_number__icontains=search))
        return Response(FederalEmployerRegistrySerializer(queryset[:500], many=True).data)


class FederalFoodHandlerSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=dict)
    def get(self, request):
        handlers = FoodHandlerProfile.objects.all()
        return Response(
            {
                "totals": {"registered_handlers": handlers.count()},
                "by_state": list(handlers.values("state__id", "state__name").annotate(total=Count("id")).order_by("state__name")),
                "by_category": list(handlers.values("food_handler_category").annotate(total=Count("id")).order_by("food_handler_category")),
                "by_status": list(handlers.values("current_status").annotate(total=Count("id")).order_by("current_status")),
            }
        )


class FederalPolicyView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    def get_object(self):
        config = NationalPolicyConfig.objects.order_by("-created_at").first()
        if config:
            return config
        return NationalPolicyConfig.objects.create()

    @extend_schema(responses=NationalPolicyConfigSerializer)
    def get(self, request):
        return Response(NationalPolicyConfigSerializer(self.get_object()).data)

    @extend_schema(request=NationalPolicyConfigSerializer, responses=NationalPolicyConfigSerializer)
    def patch(self, request):
        if not can_manage_national_policy(request.user):
            raise PermissionDenied("You cannot manage national policy.")
        serializer = NationalPolicyConfigSerializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        config = serializer.save(updated_by=request.user)
        log_action(action=AuditAction.UPDATE, actor=request.user, target=config, metadata={"event": "national_policy_updated"})
        return Response(NationalPolicyConfigSerializer(config).data)


class FederalStateOverrideView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=StatePolicyConfigSerializer(many=True))
    def get(self, request):
        queryset = StatePolicyConfig.objects.select_related("state", "updated_by").order_by("state__name")
        return Response(StatePolicyConfigSerializer(queryset, many=True).data)


class FederalIndicatorsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(FederalOversightService.indicators())


class FederalDataQualityView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(FederalOversightService.data_quality())


class FederalAuditLogView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(
            FederalOversightService.audit_logs(
                action=request.query_params.get("action", ""),
                state=request.query_params.get("state", ""),
                search=request.query_params.get("search", ""),
            )
        )


class FederalQueryListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    def get_queryset(self):
        queryset = FederalStateQuery.objects.select_related("state", "raised_by", "assigned_to", "responded_by").order_by("-created_at")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        state = self.request.query_params.get("state")
        if state:
            queryset = queryset.filter(state_id=state)
        return queryset

    @extend_schema(responses=FederalStateQuerySerializer(many=True))
    def get(self, request):
        return Response(FederalStateQuerySerializer(self.get_queryset(), many=True).data)

    @extend_schema(request=FederalStateQueryCreateSerializer, responses={201: FederalStateQuerySerializer})
    def post(self, request):
        if not can_manage_federal_queries(request.user):
            raise PermissionDenied("You cannot create federal state queries.")
        serializer = FederalStateQueryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.save(raised_by=request.user)
        log_action(action=AuditAction.WORKFLOW_TRANSITION, actor=request.user, target=query, state=query.state, metadata={"event": "federal_state_query_created"})
        return Response(FederalStateQuerySerializer(query).data, status=status.HTTP_201_CREATED)


class FederalQueryRespondView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(request=FederalStateQueryResponseSerializer, responses=FederalStateQuerySerializer)
    def patch(self, request, pk):
        if not can_manage_federal_queries(request.user):
            raise PermissionDenied("You cannot respond to federal state queries.")
        query = get_object_or_404(FederalStateQuery.objects.select_related("state"), pk=pk)
        serializer = FederalStateQueryResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(FederalStateQuerySerializer(FederalOversightService.respond_query(query=query, actor=request.user, response=serializer.validated_data["response"])).data)


class FederalQueryCloseView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    @extend_schema(responses=FederalStateQuerySerializer)
    def patch(self, request, pk):
        if not can_manage_federal_queries(request.user):
            raise PermissionDenied("You cannot close federal state queries.")
        query = get_object_or_404(FederalStateQuery.objects.select_related("state"), pk=pk)
        return Response(FederalStateQuerySerializer(FederalOversightService.close_query(query=query, actor=request.user)).data)


class StateOrganizationMixin:
    def get_state_organization(self):
        organization = get_state_ministry_organization(self.request.user)
        if not organization:
            raise PermissionDenied("Your account is not assigned to a state ministry.")
        return organization

    def get_unit_queryset(self):
        return OrganizationUnit.objects.select_related("organization", "parent", "state", "lga").filter(
            organization=self.get_state_organization()
        )


class StateUnitListCreateView(StateOrganizationMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=OrganizationUnitSerializer(many=True))
    def get(self, request):
        serializer = OrganizationUnitSerializer(self.get_unit_queryset(), many=True)
        return Response(serializer.data)

    @extend_schema(request=OrganizationUnitSerializer, responses={201: OrganizationUnitSerializer})
    def post(self, request):
        if not can_manage_state_users(request.user):
            raise PermissionDenied("You cannot manage state ministry units.")
        serializer = OrganizationUnitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unit = create_unit(actor=request.user, organization=self.get_state_organization(), **serializer.validated_data)
        return Response(OrganizationUnitSerializer(unit).data, status=status.HTTP_201_CREATED)


class StateUnitDetailView(StateOrganizationMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    def get_object(self, pk):
        return get_object_or_404(self.get_unit_queryset(), pk=pk)

    @extend_schema(responses=OrganizationUnitSerializer)
    def get(self, request, pk):
        return Response(OrganizationUnitSerializer(self.get_object(pk)).data)

    @extend_schema(request=OrganizationUnitSerializer, responses=OrganizationUnitSerializer)
    def patch(self, request, pk):
        if not can_manage_state_users(request.user):
            raise PermissionDenied("You cannot manage state ministry units.")
        instance = self.get_object(pk)
        serializer = OrganizationUnitSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        unit = update_unit(actor=request.user, unit=instance, **serializer.validated_data)
        return Response(OrganizationUnitSerializer(unit).data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        if not can_manage_state_users(request.user):
            raise PermissionDenied("You cannot manage state ministry units.")
        deactivate_unit(actor=request.user, unit=self.get_object(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)


class StateUserListView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=StateMinistryUserSerializer(many=True))
    def get(self, request):
        if not request.user.state_id:
            raise PermissionDenied("Your account is not assigned to a state.")
        queryset = User.objects.select_related("organization", "unit", "state", "ministry_profile").filter(
            state=request.user.state,
            role__in=["state_admin", "inspector"],
        ).order_by("first_name", "last_name", "email")
        return Response(StateMinistryUserSerializer(queryset, many=True).data)


class StateInviteListCreateView(StateOrganizationMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=StateMinistryInviteSerializer(many=True))
    def get(self, request):
        queryset = UserInvite.objects.select_related("organization", "unit", "invited_by", "accepted_by").filter(
            organization=self.get_state_organization()
        )
        return Response(StateMinistryInviteSerializer(queryset, many=True).data)

    @extend_schema(request=StateMinistryInviteCreateSerializer, responses={201: StateMinistryInviteSerializer})
    def post(self, request):
        if not can_manage_state_users(request.user):
            raise PermissionDenied("You cannot invite state ministry users.")
        serializer = StateMinistryInviteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        organization = self.get_state_organization()
        unit = serializer.validated_data.get("unit")
        if unit and unit.organization_id != organization.id:
            raise ValidationError("Invite unit must belong to your state ministry organization.")
        invite = InviteService.create_invite(
            actor=request.user,
            organization=organization,
            email=serializer.validated_data["email"],
            role=serializer.validated_data["role"],
            unit=unit,
            phone=serializer.validated_data.get("phone", ""),
            message=serializer.validated_data.get("message", ""),
            expires_at=serializer.validated_data.get("expires_at"),
            ministry_staff_role=serializer.validated_data.get("ministry_staff_role", ""),
        )
        return Response(StateMinistryInviteSerializer(invite).data, status=status.HTTP_201_CREATED)


class StateInviteDetailView(StateOrganizationMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    def get_object(self, pk):
        return get_object_or_404(
            UserInvite.objects.select_related("organization", "unit", "invited_by", "accepted_by").filter(
                organization=self.get_state_organization()
            ),
            pk=pk,
        )

    @extend_schema(responses=StateMinistryInviteSerializer)
    def get(self, request, pk):
        return Response(StateMinistryInviteSerializer(self.get_object(pk)).data)

    @extend_schema(responses=StateMinistryInviteSerializer)
    def delete(self, request, pk):
        if not can_manage_state_users(request.user):
            raise PermissionDenied("You cannot revoke state ministry invites.")
        invite = InviteService.revoke(invite=self.get_object(pk), actor=request.user)
        return Response(StateMinistryInviteSerializer(invite).data)


class StateFacilityMixin:
    def state_facilities(self):
        user = self.request.user
        if not user.state_id:
            raise PermissionDenied("Your account is not assigned to a state.")
        queryset = MedicalFacility.objects.select_related("organization", "state", "lga", "approved_by").filter(state=user.state)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(accreditation_status=status_filter)
        facility_type = self.request.query_params.get("facility_type")
        if facility_type:
            queryset = queryset.filter(facility_type=facility_type)
        lga = self.request.query_params.get("lga")
        if lga:
            queryset = queryset.filter(lga_id=lga)
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(facility_name__icontains=search)
        return queryset.order_by("facility_name")

    def state_applications(self):
        queryset = FacilityAccreditationApplication.objects.select_related(
            "facility",
            "facility__organization",
            "facility__state",
            "facility__lga",
            "reviewer",
        ).filter(facility__in=self.state_facilities())
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(application_status=status_filter)
        queue = self.request.query_params.get("queue")
        if queue == "pending":
            queryset = queryset.filter(application_status__in=[AccreditationStatus.SUBMITTED, AccreditationStatus.UNDER_REVIEW])
        return queryset.order_by("-created_at")

    def ensure_reviewer(self):
        if not can_review_facility_accreditation(self.request.user):
            raise PermissionDenied("You cannot review facility accreditation.")

    def latest_application_for_facility(self, facility_id):
        facility = get_object_or_404(self.state_facilities(), pk=facility_id)
        return (
            FacilityAccreditationApplication.objects.select_related("facility", "reviewer")
            .filter(facility=facility)
            .order_by("-created_at")
            .first()
        )

    def perform_application_action(self, application, action):
        self.ensure_reviewer()
        if not application:
            raise ValidationError("This facility has no accreditation application.")
        review_comment = self.request.data.get("review_comment", "")
        if action in {"reject", "suspend"} and not review_comment.strip():
            raise ValidationError("A review comment is required for this action.")
        actions = {
            "approve": FacilityAccreditationService.approve,
            "reject": FacilityAccreditationService.reject,
            "suspend": FacilityAccreditationService.suspend,
            "reinstate": FacilityAccreditationService.reactivate,
        }
        service_action = actions[action]
        return service_action(application=application, reviewer=self.request.user, review_comment=review_comment)


class StateFacilityListView(StateFacilityMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=MedicalFacilitySerializer(many=True))
    def get(self, request):
        return Response(MedicalFacilitySerializer(self.state_facilities(), many=True).data)


class StateFacilityApplicationListView(StateFacilityMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=FacilityAccreditationApplicationSerializer(many=True))
    def get(self, request):
        return Response(FacilityAccreditationApplicationSerializer(self.state_applications(), many=True).data)


class StateFacilityApplicationActionView(StateFacilityMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]
    action_name = ""

    @extend_schema(responses=FacilityAccreditationApplicationSerializer)
    def patch(self, request, pk):
        application = get_object_or_404(self.state_applications(), pk=pk)
        application = self.perform_application_action(application, self.action_name)
        return Response(FacilityAccreditationApplicationSerializer(application).data)


class StateFacilityActionView(StateFacilityMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]
    action_name = ""

    @extend_schema(responses=FacilityAccreditationApplicationSerializer)
    def patch(self, request, pk):
        application = self.latest_application_for_facility(pk)
        application = self.perform_application_action(application, self.action_name)
        return Response(FacilityAccreditationApplicationSerializer(application).data)


class StateFacilityApproveView(StateFacilityActionView):
    action_name = "approve"


class StateFacilityRejectView(StateFacilityActionView):
    action_name = "reject"


class StateFacilitySuspendView(StateFacilityActionView):
    action_name = "suspend"


class StateFacilityReinstateView(StateFacilityActionView):
    action_name = "reinstate"


class StateFacilityApplicationApproveView(StateFacilityApplicationActionView):
    action_name = "approve"


class StateFacilityApplicationRejectView(StateFacilityApplicationActionView):
    action_name = "reject"


class StateFacilityApplicationSuspendView(StateFacilityApplicationActionView):
    action_name = "suspend"


class StateFacilityApplicationReinstateView(StateFacilityApplicationActionView):
    action_name = "reinstate"


class StateAssessmentFeeListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    def get_queryset(self):
        user = self.request.user
        if not user.state_id:
            raise PermissionDenied("Your account is not assigned to a state.")
        queryset = AssessmentFee.objects.select_related("state", "created_by").filter(state=user.state)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        facility_type = self.request.query_params.get("facility_type")
        if facility_type:
            queryset = queryset.filter(facility_type=facility_type)
        return queryset.order_by("-effective_from", "-created_at")

    def validate_fee_split(self, data):
        total = data["state_fee"] + data["facility_fee"]
        if total != data["amount"]:
            raise ValidationError("State and facility fees must equal the state assessment amount. Platform fees are configured by the platform owner and added at checkout.")

    def validate_no_overlap(self, *, facility_type, effective_from, effective_to=None, exclude=None):
        queryset = self.get_queryset().filter(
            facility_type=facility_type,
            status__in=[ActiveStatus.ACTIVE, ActiveStatus.SCHEDULED],
        )
        if exclude:
            queryset = queryset.exclude(pk=exclude.pk)
        if effective_to is None:
            overlap = queryset.filter(effective_to__isnull=True) | queryset.filter(effective_to__gte=effective_from)
        else:
            overlap = queryset.filter(effective_from__lte=effective_to).filter(
                Q(effective_to__isnull=True) | Q(effective_to__gte=effective_from)
            )
        if overlap.exists():
            raise ValidationError("Active or scheduled fee periods cannot overlap for the same facility type.")

    def validate_not_used_for_financial_change(self, fee, data):
        financial_fields = {
            "facility_type",
            "amount",
            "currency",
            "state_fee",
            "facility_fee",
            "provider_fee_handling",
            "effective_from",
            "effective_to",
        }
        if not financial_fields.intersection(data):
            return
        if PaymentTransaction.objects.filter(metadata__assessment_fee_id=str(fee.id)).exists():
            raise ValidationError("Fee schedules used by payments cannot be edited. Create a replacement schedule instead.")

    @extend_schema(responses=AssessmentFeeSerializer(many=True))
    def get(self, request):
        return Response(AssessmentFeeSerializer(self.get_queryset(), many=True).data)

    @extend_schema(request=AssessmentFeeSerializer, responses={201: AssessmentFeeSerializer})
    def post(self, request):
        if not can_manage_state_fees(request.user):
            raise PermissionDenied("You cannot configure state assessment fees.")
        serializer = AssessmentFeeSerializer(data={**request.data, "state": str(request.user.state_id)})
        serializer.is_valid(raise_exception=True)
        self.validate_fee_split(serializer.validated_data)
        if serializer.validated_data.get("status") in {ActiveStatus.ACTIVE, ActiveStatus.SCHEDULED}:
            self.validate_no_overlap(
                facility_type=serializer.validated_data["facility_type"],
                effective_from=serializer.validated_data["effective_from"],
                effective_to=serializer.validated_data.get("effective_to"),
            )
        fee = serializer.save(state=request.user.state, created_by=request.user)
        return Response(AssessmentFeeSerializer(fee).data, status=status.HTTP_201_CREATED)


class StateAssessmentFeeDetailView(StateAssessmentFeeListCreateView):
    def get_object(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)

    @extend_schema(request=AssessmentFeeSerializer, responses=AssessmentFeeSerializer)
    def patch(self, request, pk):
        if not can_manage_state_fees(request.user):
            raise PermissionDenied("You cannot configure state assessment fees.")
        fee = self.get_object(pk)
        serializer = AssessmentFeeSerializer(fee, data={**request.data, "state": str(request.user.state_id)}, partial=True)
        serializer.is_valid(raise_exception=True)
        values = {
            "amount": serializer.validated_data.get("amount", fee.amount),
            "state_fee": serializer.validated_data.get("state_fee", fee.state_fee),
            "facility_fee": serializer.validated_data.get("facility_fee", fee.facility_fee),
        }
        self.validate_fee_split(values)
        facility_type = serializer.validated_data.get("facility_type", fee.facility_type)
        effective_from = serializer.validated_data.get("effective_from", fee.effective_from)
        effective_to = serializer.validated_data.get("effective_to", fee.effective_to)
        status_value = serializer.validated_data.get("status", fee.status)
        self.validate_not_used_for_financial_change(fee, serializer.validated_data)
        if status_value in {ActiveStatus.ACTIVE, ActiveStatus.SCHEDULED}:
            self.validate_no_overlap(
                facility_type=facility_type,
                effective_from=effective_from,
                effective_to=effective_to,
                exclude=fee,
            )
        fee = serializer.save(state=request.user.state)
        return Response(AssessmentFeeSerializer(fee).data)

    def post(self, request, pk, action=None):
        if not can_manage_state_fees(request.user):
            raise PermissionDenied("You cannot configure state assessment fees.")
        fee = self.get_object(pk)
        if action == "submit":
            if fee.status not in {ActiveStatus.DRAFT, ActiveStatus.INACTIVE}:
                raise ValidationError("Only draft or inactive fee schedules can be submitted.")
            fee.status = ActiveStatus.PENDING_APPROVAL
            update_fields = ["status", "updated_at"]
            event = "fee_schedule_submitted"
        elif action == "approve":
            self.validate_no_overlap(
                facility_type=fee.facility_type,
                effective_from=fee.effective_from,
                effective_to=fee.effective_to,
                exclude=fee,
            )
            fee.status = ActiveStatus.ACTIVE if fee.effective_from <= timezone.localdate() else ActiveStatus.SCHEDULED
            fee.approved_by = request.user
            fee.approved_at = timezone.now()
            update_fields = ["status", "approved_by", "approved_at", "updated_at"]
            event = "fee_schedule_approved"
        elif action == "suspend":
            fee.status = ActiveStatus.SUSPENDED
            update_fields = ["status", "updated_at"]
            event = "fee_schedule_suspended"
        else:
            raise ValidationError("Unsupported fee schedule action.")
        fee.save(update_fields=update_fields)
        log_action(action=AuditAction.UPDATE, actor=request.user, target=fee, metadata={"event": event})
        return Response(AssessmentFeeSerializer(fee).data)


class StateCertificateValidationMixin:
    def get_queryset(self):
        user = self.request.user
        if not user.state_id:
            raise PermissionDenied("Your account is not assigned to a state.")
        queryset = CertificateRequest.objects.select_related(
            "assessment",
            "assessment__food_handler",
            "assessment__employer",
            "assessment__facility",
            "assessment__facility__state",
            "assessment__payment_transaction",
            "assessment__certificate",
            "requested_by",
            "reviewed_by",
        ).filter(assessment__facility__state=user.state)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        facility = self.request.query_params.get("facility")
        if facility:
            queryset = queryset.filter(assessment__facility_id=facility)
        date_from = self.request.query_params.get("date_from")
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        date_to = self.request.query_params.get("date_to")
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        return queryset.order_by("-created_at")

    def get_object(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)

    def ensure_validator(self):
        if not can_validate_certificates(self.request.user):
            raise PermissionDenied("You cannot validate certificate requests.")

    def action_notes(self):
        serializer = StateCertificateValidationActionSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data.get("review_notes", "")


class StateCertificateValidationListView(StateCertificateValidationMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=StateCertificateValidationSerializer(many=True))
    def get(self, request):
        return Response(StateCertificateValidationSerializer(self.get_queryset(), many=True).data)


class StateCertificateValidationDetailView(StateCertificateValidationMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=StateCertificateValidationSerializer)
    def get(self, request, pk):
        return Response(StateCertificateValidationSerializer(self.get_object(pk)).data)


class StateCertificateValidationApproveView(StateCertificateValidationMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(request=StateCertificateValidationActionSerializer, responses=StateCertificateValidationSerializer)
    def patch(self, request, pk):
        self.ensure_validator()
        certificate_request, _certificate = CertificateService.approve_and_generate(
            request=self.get_object(pk),
            reviewer=request.user,
            notes=self.action_notes(),
        )
        certificate_request.refresh_from_db()
        return Response(StateCertificateValidationSerializer(certificate_request).data)


class StateCertificateValidationRejectView(StateCertificateValidationMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(request=StateCertificateValidationActionSerializer, responses=StateCertificateValidationSerializer)
    def patch(self, request, pk):
        self.ensure_validator()
        notes = self.action_notes()
        if not notes.strip():
            raise ValidationError("Review notes are required when rejecting a certificate request.")
        certificate_request = CertificateService.reject_request(
            request=self.get_object(pk),
            reviewer=request.user,
            notes=notes,
        )
        return Response(StateCertificateValidationSerializer(certificate_request).data)


class StateCertificateValidationClarificationView(StateCertificateValidationMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(request=StateCertificateValidationActionSerializer, responses=StateCertificateValidationSerializer)
    def patch(self, request, pk):
        self.ensure_validator()
        notes = self.action_notes()
        if not notes.strip():
            raise ValidationError("Review notes are required when requesting clarification.")
        certificate_request = CertificateService.request_clarification(
            request=self.get_object(pk),
            reviewer=request.user,
            notes=notes,
        )
        return Response(StateCertificateValidationSerializer(certificate_request).data)


class StateCertificateRegistryMixin:
    def get_queryset(self):
        user = self.request.user
        if not user.state_id:
            raise PermissionDenied("Your account is not assigned to a state.")
        queryset = Certificate.objects.select_related(
            "food_handler",
            "employer",
            "facility",
            "issuing_state",
            "revoked_by",
        ).filter(issuing_state=user.state)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            if status_filter == CertificateStatus.EXPIRED:
                queryset = queryset.filter(status=CertificateStatus.ACTIVE, expiry_date__lt=timezone.localdate())
            else:
                queryset = queryset.filter(status=status_filter)
        facility = self.request.query_params.get("facility")
        if facility:
            queryset = queryset.filter(facility_id=facility)
        employer = self.request.query_params.get("employer")
        if employer:
            queryset = queryset.filter(employer_id=employer)
        expiry_window = self.request.query_params.get("expiry_window")
        if expiry_window == "expired":
            queryset = queryset.filter(expiry_date__lt=timezone.localdate())
        elif expiry_window:
            try:
                days = int(expiry_window)
                queryset = queryset.filter(
                    expiry_date__gte=timezone.localdate(),
                    expiry_date__lte=timezone.localdate() + timezone.timedelta(days=days),
                )
            except ValueError:
                raise ValidationError("Expiry window must be a number of days or 'expired'.")
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(certificate_number__icontains=search)
                | Q(food_handler__full_name__icontains=search)
                | Q(employer__business_name__icontains=search)
                | Q(facility__facility_name__icontains=search)
            )
        return queryset.order_by("-issue_date", "-created_at")

    def get_object(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)

    def lifecycle_reason(self):
        serializer = StateCertificateLifecycleActionSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data["reason"]


class StateCertificateRegistryListView(StateCertificateRegistryMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=StateCertificateRegistrySerializer(many=True))
    def get(self, request):
        return Response(StateCertificateRegistrySerializer(self.get_queryset(), many=True).data)


class StateCertificateRegistryDetailView(StateCertificateRegistryMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=StateCertificateRegistrySerializer)
    def get(self, request, pk):
        return Response(StateCertificateRegistrySerializer(self.get_object(pk)).data)


class StateCertificateSuspendView(StateCertificateRegistryMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(request=StateCertificateLifecycleActionSerializer, responses=StateCertificateRegistrySerializer)
    def patch(self, request, pk):
        certificate = CertificateService.suspend(certificate=self.get_object(pk), actor=request.user, reason=self.lifecycle_reason())
        return Response(StateCertificateRegistrySerializer(certificate).data)


class StateCertificateRevokeView(StateCertificateRegistryMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(request=StateCertificateLifecycleActionSerializer, responses=StateCertificateRegistrySerializer)
    def patch(self, request, pk):
        certificate = CertificateService.revoke(certificate=self.get_object(pk), actor=request.user, reason=self.lifecycle_reason())
        return Response(StateCertificateRegistrySerializer(certificate).data)


class StateCertificateReinstateView(StateCertificateRegistryMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(request=StateCertificateLifecycleActionSerializer, responses=StateCertificateRegistrySerializer)
    def patch(self, request, pk):
        certificate = CertificateService.reinstate(certificate=self.get_object(pk), actor=request.user, reason=self.lifecycle_reason())
        return Response(StateCertificateRegistrySerializer(certificate).data)


class StateCertificateReplaceView(StateCertificateRegistryMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(request=StateCertificateLifecycleActionSerializer, responses=StateCertificateRegistrySerializer)
    def post(self, request, pk):
        certificate = CertificateService.replace(certificate=self.get_object(pk), actor=request.user, reason=self.lifecycle_reason())
        return Response(StateCertificateRegistrySerializer(certificate).data)


class StateCertificateAuditView(StateCertificateRegistryMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    def get(self, request, pk):
        certificate = self.get_object(pk)
        logs = AuditLog.objects.filter(target_type="Certificate", target_id=str(certificate.id)).select_related("actor").order_by("-created_at")[:100]
        return Response([
            {
                "id": str(log.id),
                "action": log.action,
                "actor_name": log.actor.get_full_name() if log.actor else "",
                "metadata": log.metadata,
                "created_at": log.created_at,
            }
            for log in logs
        ])


class StateCertificateExportView(StateCertificateRegistryMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="state-certificates.csv"'
        writer = csv.writer(response)
        writer.writerow(["Certificate", "Food handler", "Employer", "Facility", "State", "Issue date", "Expiry date", "Status"])
        for cert in self.get_queryset()[:2000]:
            writer.writerow([
                cert.certificate_number,
                cert.food_handler.full_name,
                cert.employer.business_name if cert.employer_id else "",
                cert.facility.facility_name,
                cert.issuing_state.name,
                cert.issue_date.isoformat(),
                cert.expiry_date.isoformat(),
                cert.effective_status,
            ])
        log_action(action=AuditAction.CERTIFICATE_EVENT, actor=request.user, metadata={"event": "state_certificate_export"})
        return response


def _certificate_registry_row(certificate):
    return {
        "id": str(certificate.id),
        "record_type": "food_handler_certificate",
        "owner_type": "food_handler",
        "owner_id": str(certificate.food_handler_id),
        "owner_name": certificate.food_handler.full_name,
        "certificate_number": certificate.certificate_number,
        "status": certificate.effective_status,
        "issue_date": certificate.issue_date,
        "expiry_date": certificate.expiry_date,
        "issuing_state_name": certificate.issuing_state.name,
        "action_status": "",
        "source_id": str(certificate.id),
        "metadata": {
            "employer_name": certificate.employer.business_name if certificate.employer_id else "",
            "facility_name": certificate.facility.facility_name if certificate.facility_id else "",
            "verification_url": certificate.verification_url,
        },
    }


def _accreditation_registry_row(certificate):
    return {
        "id": str(certificate.id),
        "record_type": certificate.certificate_type,
        "owner_type": certificate.owner_type,
        "owner_id": str(certificate.employer_id or certificate.facility_id or ""),
        "owner_name": certificate.owner_name,
        "certificate_number": certificate.certificate_number,
        "status": certificate.effective_status,
        "issue_date": certificate.issue_date,
        "expiry_date": certificate.expiry_date,
        "issuing_state_name": certificate.issuing_state.name,
        "action_status": "",
        "source_id": str(certificate.id),
        "metadata": {"verification_url": certificate.verification_url, "certificate_type": certificate.certificate_type},
    }


def _certificate_request_registry_row(request):
    assessment = request.assessment
    try:
        certificate_number = assessment.certificate.certificate_number
    except Certificate.DoesNotExist:
        certificate_number = ""
    return {
        "id": str(request.id),
        "record_type": "food_handler_certificate_request",
        "owner_type": "food_handler",
        "owner_id": str(assessment.food_handler_id),
        "owner_name": assessment.food_handler.full_name,
        "certificate_number": certificate_number,
        "status": request.status,
        "issue_date": None,
        "expiry_date": None,
        "issuing_state_name": assessment.facility.state.name,
        "action_status": request.status,
        "source_id": str(request.id),
        "metadata": {"facility_name": assessment.facility.facility_name, "assessment_id": str(assessment.id)},
    }


def _facility_application_registry_row(application):
    return {
        "id": str(application.id),
        "record_type": "facility_accreditation_application",
        "owner_type": "facility",
        "owner_id": str(application.facility_id),
        "owner_name": application.facility.facility_name,
        "certificate_number": "",
        "status": application.application_status,
        "issue_date": None,
        "expiry_date": application.facility.accreditation_expiry_date,
        "issuing_state_name": application.facility.state.name,
        "action_status": application.application_status,
        "source_id": str(application.id),
        "metadata": {"facility_type": application.facility.facility_type, "lga_name": application.facility.lga.name if application.facility.lga_id else ""},
    }


def _employer_review_registry_row(employer):
    return {
        "id": str(employer.id),
        "record_type": "employer_accreditation_review",
        "owner_type": "employer",
        "owner_id": str(employer.id),
        "owner_name": employer.business_name,
        "certificate_number": "",
        "status": employer.compliance_status,
        "issue_date": None,
        "expiry_date": None,
        "issuing_state_name": employer.state.name,
        "action_status": employer.compliance_status,
        "source_id": str(employer.id),
        "metadata": {"registration_number": employer.business_registration_number, "lga_name": employer.lga.name if employer.lga_id else ""},
    }


class UnifiedCertificateRegistryMixin:
    permission_classes = [IsAuthenticated, IsActiveUser]

    def base_state_id(self):
        return None

    def search_filter(self, rows):
        search = self.request.query_params.get("search", "").strip().lower()
        if not search:
            return rows
        return [
            row for row in rows
            if search in " ".join([row["owner_name"], row["certificate_number"], row["status"], row["record_type"]]).lower()
        ]

    def food_handler_certificates(self):
        queryset = Certificate.objects.select_related("food_handler", "employer", "facility", "issuing_state").order_by("-issue_date", "-created_at")
        state_id = self.base_state_id()
        if state_id:
            queryset = queryset.filter(issuing_state_id=state_id)
        return [_certificate_registry_row(certificate) for certificate in queryset[:500]]

    def accreditation_certificates(self, certificate_type=None):
        queryset = AccreditationCertificate.objects.select_related("employer", "facility", "issuing_state").order_by("-issue_date", "-created_at")
        state_id = self.base_state_id()
        if state_id:
            queryset = queryset.filter(issuing_state_id=state_id)
        if certificate_type:
            queryset = queryset.filter(certificate_type=certificate_type)
        return [_accreditation_registry_row(certificate) for certificate in queryset[:500]]

    def pending_review(self):
        state_id = self.base_state_id()
        certificate_requests = CertificateRequest.objects.select_related("assessment", "assessment__food_handler", "assessment__facility", "assessment__facility__state").filter(
            status__in=[CertificateRequestStatus.PENDING_VALIDATION, CertificateRequestStatus.CORRECTION_REQUESTED],
        )
        facility_applications = FacilityAccreditationApplication.objects.select_related("facility", "facility__state", "facility__lga").filter(
            application_status__in=[AccreditationStatus.SUBMITTED, AccreditationStatus.UNDER_REVIEW],
        )
        employers = Employer.objects.select_related("state", "lga").filter(compliance_status=ComplianceStatus.UNDER_REVIEW)
        if state_id:
            certificate_requests = certificate_requests.filter(assessment__facility__state_id=state_id)
            facility_applications = facility_applications.filter(facility__state_id=state_id)
            employers = employers.filter(state_id=state_id)
        rows = [_certificate_request_registry_row(item) for item in certificate_requests[:200]]
        rows += [_facility_application_registry_row(item) for item in facility_applications[:200]]
        rows += [_employer_review_registry_row(item) for item in employers[:200]]
        return rows

    def ensure_employer_accreditation_documents(self):
        queryset = Employer.objects.select_related("state").filter(compliance_status=ComplianceStatus.COMPLIANT)
        state_id = self.base_state_id()
        if state_id:
            queryset = queryset.filter(state_id=state_id)
        for employer in queryset[:200]:
            CertificateService.issue_employer_accreditation_certificate(employer=employer, actor=self.request.user)

    def registry_rows(self):
        tab = self.request.query_params.get("tab", "pending_review")
        if tab == "pending_review":
            rows = self.pending_review()
        elif tab == "food_handler_certificates":
            rows = self.food_handler_certificates()
        elif tab == "employer_accreditation_certificates":
            self.ensure_employer_accreditation_documents()
            rows = self.accreditation_certificates(AccreditationCertificateType.EMPLOYER)
        elif tab == "facility_accreditation_certificates":
            rows = self.accreditation_certificates(AccreditationCertificateType.FACILITY)
        else:
            rows = self.pending_review() + self.food_handler_certificates() + self.accreditation_certificates()
        return self.search_filter(rows)[:500]


class StateUnifiedCertificateRegistryView(UnifiedCertificateRegistryMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    def base_state_id(self):
        if not self.request.user.state_id:
            raise PermissionDenied("Your account is not assigned to a state.")
        return self.request.user.state_id

    def get(self, request):
        return Response(self.registry_rows())


class FederalUnifiedCertificateRegistryView(UnifiedCertificateRegistryMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsFederalMinistryUser]

    def base_state_id(self):
        return self.request.query_params.get("state")

    def get(self, request):
        return Response(self.registry_rows())


class StateMonitoringMixin:
    def require_state(self):
        if not self.request.user.state_id:
            raise PermissionDenied("Your account is not assigned to a state.")
        return self.request.user.state

    def scoped_lga(self):
        return self.request.query_params.get("lga")


class StateEmployerMonitoringView(StateMonitoringMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=StateEmployerMonitoringSerializer(many=True))
    def get(self, request):
        queryset = Employer.objects.select_related("state", "lga").filter(state=self.require_state())
        lga = self.scoped_lga()
        if lga:
            queryset = queryset.filter(lga_id=lga)
        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(establishment_category=category)
        compliance_status = request.query_params.get("compliance_status")
        if compliance_status:
            queryset = queryset.filter(compliance_status=compliance_status)
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(business_name__icontains=search) | Q(business_registration_number__icontains=search))
        return Response(StateEmployerMonitoringSerializer(queryset.order_by("business_name"), many=True).data)


class StateFoodHandlerMonitoringView(StateMonitoringMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=StateFoodHandlerMonitoringSerializer(many=True))
    def get(self, request):
        queryset = FoodHandlerProfile.objects.select_related("state", "lga", "employer", "business_branch").filter(
            state=self.require_state()
        )
        lga = self.scoped_lga()
        if lga:
            queryset = queryset.filter(lga_id=lga)
        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(food_handler_category=category)
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(current_status=status_filter)
        employer = request.query_params.get("employer")
        if employer:
            queryset = queryset.filter(employer_id=employer)
        certificate_status = request.query_params.get("certificate_status")
        if certificate_status:
            if certificate_status == "not_issued":
                queryset = queryset.filter(certificates__isnull=True)
            elif certificate_status == "expired":
                queryset = queryset.filter(certificates__status=CertificateStatus.ACTIVE, certificates__expiry_date__lt=timezone.localdate())
            else:
                queryset = queryset.filter(certificates__status=certificate_status)
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(full_name__icontains=search) | Q(system_identifier__icontains=search))
        return Response(StateFoodHandlerMonitoringSerializer(queryset.distinct().order_by("full_name"), many=True).data)


class StateIllnessMonitoringView(StateMonitoringMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=StateIllnessMonitoringSerializer(many=True))
    def get(self, request):
        queryset = IllnessReport.objects.select_related("food_handler", "food_handler__lga", "employer").filter(
            food_handler__state=self.require_state()
        )
        lga = self.scoped_lga()
        if lga:
            queryset = queryset.filter(food_handler__lga_id=lga)
        clearance_status = request.query_params.get("clearance_status")
        if clearance_status:
            queryset = queryset.filter(clearance_status=clearance_status)
        active = request.query_params.get("active")
        if active == "true":
            queryset = queryset.exclude(clearance_status__in=["cleared", "rejected"])
        employer = request.query_params.get("employer")
        if employer:
            queryset = queryset.filter(employer_id=employer)
        return Response(StateIllnessMonitoringSerializer(queryset.order_by("-created_at"), many=True).data)


class StateInspectionMixin(StateMonitoringMixin):
    def get_queryset(self):
        state = self.require_state()
        queryset = Inspection.objects.select_related(
            "inspector",
            "employer",
            "employer__state",
            "employer__lga",
            "branch",
        ).prefetch_related("employer_responses").filter(employer__state=state)
        lga = self.scoped_lga()
        if lga:
            queryset = queryset.filter(employer__lga_id=lga)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        enforcement_action = self.request.query_params.get("enforcement_action")
        if enforcement_action:
            queryset = queryset.filter(enforcement_action=enforcement_action)
        inspector = self.request.query_params.get("inspector")
        if inspector:
            queryset = queryset.filter(inspector_id=inspector)
        employer = self.request.query_params.get("employer")
        if employer:
            queryset = queryset.filter(employer_id=employer)
        queue = self.request.query_params.get("queue")
        if queue == "active":
            queryset = queryset.exclude(status=InspectionStatus.CLOSED)
        elif queue == "submitted":
            queryset = queryset.filter(status__in=[InspectionStatus.SUBMITTED, InspectionStatus.EMPLOYER_RESPONSE_SUBMITTED])
        elif queue == "enforcement":
            queryset = queryset.exclude(enforcement_action="none")
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(employer__business_name__icontains=search)
                | Q(inspector__first_name__icontains=search)
                | Q(inspector__last_name__icontains=search)
                | Q(findings__icontains=search)
            )
        return queryset.order_by("-inspection_date", "-created_at")

    def get_object(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)

    def ensure_coordinator(self):
        if not can_assign_inspections(self.request.user):
            raise PermissionDenied("You cannot coordinate state inspections.")


class StateInspectionListView(StateInspectionMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=StateInspectionSerializer(many=True))
    def get(self, request):
        return Response(StateInspectionSerializer(self.get_queryset(), many=True).data)

    @extend_schema(request=StateInspectionAssignmentSerializer, responses={201: StateInspectionSerializer})
    def post(self, request):
        self.ensure_coordinator()
        serializer = StateInspectionAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employer = serializer.validated_data["employer"]
        inspector = serializer.validated_data["inspector"]
        if employer.state_id != request.user.state_id:
            raise PermissionDenied("You can only assign inspections in your state.")
        data = dict(serializer.validated_data)
        data.pop("inspector", None)
        form_template = data.pop("form_template", None)
        if form_template and request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            if request.user.organization_id and form_template.owner_organization_id != request.user.organization_id:
                raise PermissionDenied("You can only assign inspection forms owned by your ministry.")
            if not request.user.organization_id and form_template.owner_organization.state_id != request.user.state_id:
                raise PermissionDenied("You can only assign inspection forms owned by your state.")
        inspection = InspectionService.assign(
            actor=request.user,
            inspector=inspector,
            **data,
        )
        if form_template:
            InspectionService.assign_form_template(
                inspection=inspection,
                actor=request.user,
                template=form_template,
            )
        return Response(StateInspectionSerializer(inspection).data, status=status.HTTP_201_CREATED)


class StateInspectionDetailView(StateInspectionMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=StateInspectionSerializer)
    def get(self, request, pk):
        return Response(StateInspectionSerializer(self.get_object(pk)).data)


class StateInspectionReviewView(StateInspectionMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(request=StateInspectionReviewSerializer, responses=StateInspectionSerializer)
    def patch(self, request, pk):
        self.ensure_coordinator()
        serializer = StateInspectionReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inspection = InspectionService.review(
            inspection=self.get_object(pk),
            actor=request.user,
            **serializer.validated_data,
        )
        return Response(StateInspectionSerializer(inspection).data)


class StateInspectionCloseView(StateInspectionMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(request=StateInspectionCloseSerializer, responses=StateInspectionSerializer)
    def patch(self, request, pk):
        self.ensure_coordinator()
        serializer = StateInspectionCloseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inspection = InspectionService.close(
            inspection=self.get_object(pk),
            actor=request.user,
            closure_notes=serializer.validated_data.get("closure_notes", ""),
        )
        return Response(StateInspectionSerializer(inspection).data)


class StateReportMixin(StateMonitoringMixin):
    def get_queryset(self):
        state = self.require_state()
        queryset = StateReport.objects.select_related("state", "generated_by", "submitted_by", "reviewed_by").filter(state=state)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        report_type = self.request.query_params.get("report_type")
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        return queryset.order_by("-reporting_period_end", "-created_at")

    def get_object(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)

    def ensure_reporter(self):
        if not can_submit_state_reports(self.request.user):
            raise PermissionDenied("You cannot generate or submit state reports.")


class StateReportListView(StateReportMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=StateReportSerializer(many=True))
    def get(self, request):
        return Response(StateReportSerializer(self.get_queryset(), many=True).data)


class StateReportGenerateView(StateReportMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(request=StateReportGenerateSerializer, responses={201: StateReportSerializer})
    def post(self, request):
        self.ensure_reporter()
        serializer = StateReportGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = StateReportService.generate(
            actor=request.user,
            report_type=serializer.validated_data["report_type"],
            period_start=serializer.validated_data["reporting_period_start"],
            period_end=serializer.validated_data["reporting_period_end"],
        )
        return Response(StateReportSerializer(report).data, status=status.HTTP_201_CREATED)


class StateReportSubmitView(StateReportMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=StateReportSerializer)
    def patch(self, request, pk):
        self.ensure_reporter()
        report = StateReportService.submit(report=self.get_object(pk), actor=request.user)
        return Response(StateReportSerializer(report).data)


class StateRevenueView(StateMonitoringMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(
            StateReportService.finance_snapshot(
                state=self.require_state(),
                date_from=request.query_params.get("date_from"),
                date_to=request.query_params.get("date_to"),
            )
        )


class StateFinanceDashboardView(StateMonitoringMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(
            StateReportService.finance_snapshot(
                state=self.require_state(),
                date_from=request.query_params.get("date_from"),
                date_to=request.query_params.get("date_to"),
            )
        )


class StateFinanceExportView(StateMonitoringMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    def get(self, request):
        snapshot = StateReportService.finance_snapshot(
            state=self.require_state(),
            date_from=request.query_params.get("date_from"),
            date_to=request.query_params.get("date_to"),
        )
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="state-finance-summary.csv"'
        writer = csv.writer(response)
        writer.writerow(["metric", "value"])
        for key, value in snapshot["cards"].items():
            writer.writerow([key, value])
        return response


class StateRefundListView(StateMonitoringMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=RefundRequestSerializer(many=True))
    def get(self, request):
        queryset = RefundRequest.objects.select_related("payment_transaction", "requested_by", "approved_by").filter(
            payment_transaction__metadata__state_id=str(self.require_state().id)
        )
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return Response(RefundRequestSerializer(queryset.order_by("-created_at")[:500], many=True).data)


class StateSettlementListView(StateMonitoringMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, IsStateMinistryUser]

    @extend_schema(responses=SettlementSerializer(many=True))
    def get(self, request):
        queryset = Settlement.objects.select_related("facility", "state", "payment_transaction").filter(state=self.require_state())
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(settlement_status=status_filter)
        facility = request.query_params.get("facility")
        if facility:
            queryset = queryset.filter(facility_id=facility)
        date_from = request.query_params.get("date_from")
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        date_to = request.query_params.get("date_to")
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        return Response(SettlementSerializer(queryset.order_by("-created_at"), many=True).data)
