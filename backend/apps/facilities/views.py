import json
import secrets
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import InviteStatus, UserInvite, UserRole, UserStatus
from apps.accounts.permissions import IsActiveUser
from apps.assessments.models import Appointment
from apps.assessments.serializers import (
    AssessmentAssignDoctorSerializer,
    AppointmentAssignDoctorSerializer,
    AppointmentRescheduleSerializer,
    AppointmentSerializer,
    AppointmentTransitionSerializer,
    FacilityAssessmentDetailSerializer,
    FacilityAssessmentSerializer,
)
from apps.assessments.services import AssessmentService
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.certificates.serializers import CertificateClarificationResponseSerializer, CertificateRequestSerializer, RequestCertificateSerializer
from apps.certificates.services import CertificateService
from apps.facilities.models import AccreditationStatus, FacilityAccreditationApplication, FacilityDocument, FacilityStaffProfile, MedicalFacility
from apps.facilities.serializers import (
    AccreditationReviewSerializer,
    FacilityAccreditationApplicationSerializer,
    FacilityDocumentSerializer,
    FacilityInviteSerializer,
    FacilityStaffInviteSerializer,
    FacilityStaffProfileSerializer,
    MedicalFacilitySerializer,
)
from apps.facilities.services import FacilityAccreditationService, FacilityProfileService
from apps.organizations.models import OrganizationUnit
from apps.organizations.serializers import OrganizationUnitSerializer
from apps.organizations.services import create_unit, deactivate_unit, update_unit
from apps.reports.serializers import DashboardQuerySerializer, GeneratedReportSerializer, GenerateReportSerializer
from apps.reports.models import ReportType
from apps.reports.services import DashboardService, ReportService


class MedicalFacilityViewSet(viewsets.ModelViewSet):
    queryset = MedicalFacility.objects.select_related("organization", "state", "lga", "approved_by").order_by("-created_at")
    serializer_class = MedicalFacilitySerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE")

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        queryset = self.queryset
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return queryset.filter(state=user.state)
        if user.organization_id:
            return queryset.filter(organization=user.organization)
        return queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != UserRole.FACILITY_ADMIN:
            raise PermissionDenied("Only facility admins can register a medical facility.")
        if MedicalFacility.objects.filter(organization=user.organization).exists():
            raise ValidationError("This organization already has a medical facility.")
        facility = serializer.save(organization=user.organization, state=user.state or serializer.validated_data["state"])
        log_action(action=AuditAction.CREATE, actor=user, target=facility)

    def perform_update(self, serializer):
        facility = self.get_object()
        user = self.request.user
        if user.role == UserRole.FACILITY_ADMIN and facility.organization_id != user.organization_id:
            raise PermissionDenied("You can only update your facility.")
        if user.role == UserRole.STATE_ADMIN and facility.state_id != user.state_id:
            raise PermissionDenied("State admins can only update facilities in their state.")
        updated = serializer.save()
        log_action(action=AuditAction.UPDATE, actor=user, target=updated)

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        if request.user.role != UserRole.FACILITY_ADMIN:
            raise PermissionDenied("Only facility admins can access the current facility profile.")
        facility = FacilityProfileService.get_for_user(request.user)
        if not facility:
            raise ValidationError("No medical facility profile exists for this organization.")
        if request.method == "GET":
            return Response(MedicalFacilitySerializer(facility).data)

        serializer = MedicalFacilitySerializer(facility, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        facility = FacilityProfileService.update_profile(
            facility=facility,
            actor=request.user,
            data=serializer.validated_data,
        )
        return Response(MedicalFacilitySerializer(facility).data)

    @action(detail=True, methods=["get"], url_path="dashboard")
    def dashboard(self, request, pk=None):
        facility = self.get_object()
        serializer = DashboardQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        payload = DashboardService.facility_dashboard(
            request.user,
            facility_id=facility.id,
            department_id=serializer.validated_data.get("department"),
            date_from=serializer.validated_data.get("date_from"),
            date_to=serializer.validated_data.get("date_to"),
            doctor_id=serializer.validated_data.get("doctor"),
            lab_status=serializer.validated_data.get("lab_status", ""),
            assessment_status=serializer.validated_data.get("assessment_status", ""),
            employer_category=serializer.validated_data.get("employer_category", ""),
        )
        return Response(payload)

    @action(detail=True, methods=["get"], url_path="reports/performance")
    def performance_report(self, request, pk=None):
        facility = self.get_object()
        serializer = GenerateReportSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data.get("filters", {})
        if isinstance(filters, str):
            filters = json.loads(filters) if filters else {}
        filters["facility"] = str(facility.id)
        report = ReportService.generate(
            report_type=ReportType.FACILITY_PERFORMANCE,
            user=request.user,
            file_format=serializer.validated_data.get("file_format", "json"),
            filters=filters,
        )
        return Response(GeneratedReportSerializer(report).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="re-accreditation")
    def re_accreditation(self, request, pk=None):
        facility = self.get_object()
        if request.user.role != UserRole.FACILITY_ADMIN or facility.organization_id != request.user.organization_id:
            raise PermissionDenied("Only the facility admin can start re-accreditation for their facility.")
        if facility.accreditation_status not in {
            AccreditationStatus.APPROVED,
            AccreditationStatus.REACCREDITATION_DUE,
            AccreditationStatus.EXPIRED,
        }:
            raise ValidationError("Only approved, expired, or re-accreditation-due facilities can start renewal.")
        if facility.accreditation_applications.filter(
            is_renewal=True,
            application_status__in=[
                AccreditationStatus.DRAFT,
                AccreditationStatus.SUBMITTED,
                AccreditationStatus.UNDER_REVIEW,
                AccreditationStatus.MORE_INFORMATION_REQUIRED,
            ],
        ).exists():
            raise ValidationError("This facility already has an active renewal application.")
        renewal = FacilityAccreditationService.create_renewal(facility=facility, actor=request.user)
        return Response(FacilityAccreditationApplicationSerializer(renewal).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="departments")
    def departments(self, request, pk=None):
        facility = self.get_object()
        queryset = OrganizationUnit.objects.select_related("organization", "parent", "state", "lga").filter(
            organization=facility.organization
        )
        if request.method == "GET":
            return Response(OrganizationUnitSerializer(queryset, many=True).data)
        serializer = OrganizationUnitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unit = create_unit(actor=request.user, organization=facility.organization, **serializer.validated_data)
        return Response(OrganizationUnitSerializer(unit).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["get", "patch", "delete"],
        url_path=r"departments/(?P<department_id>[^/.]+)",
    )
    def department_detail(self, request, pk=None, department_id=None):
        facility = self.get_object()
        unit = get_object_or_404(
            OrganizationUnit.objects.select_related("organization", "parent", "state", "lga"),
            id=department_id,
            organization=facility.organization,
        )
        if request.method == "GET":
            return Response(OrganizationUnitSerializer(unit).data)
        if request.method == "DELETE":
            deactivate_unit(actor=request.user, unit=unit)
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = OrganizationUnitSerializer(unit, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        unit = update_unit(actor=request.user, unit=unit, **serializer.validated_data)
        return Response(OrganizationUnitSerializer(unit).data)

    @action(detail=True, methods=["get"], url_path="staff")
    def staff(self, request, pk=None):
        if request.user.role != UserRole.FACILITY_ADMIN:
            raise PermissionDenied("Only facility admins can manage facility staff.")
        facility = self.get_object()
        profiles = FacilityStaffProfile.objects.select_related("user", "facility", "department").filter(facility=facility)
        return Response(FacilityStaffProfileSerializer(profiles, many=True, context={"facility": facility}).data)

    @action(detail=True, methods=["patch"], url_path=r"staff/(?P<staff_profile_id>[^/.]+)")
    def staff_detail(self, request, pk=None, staff_profile_id=None):
        if request.user.role != UserRole.FACILITY_ADMIN:
            raise PermissionDenied("Only facility admins can manage facility staff.")
        facility = self.get_object()
        profile = get_object_or_404(
            FacilityStaffProfile.objects.select_related("user", "facility", "department"),
            id=staff_profile_id,
            facility=facility,
        )
        serializer = FacilityStaffProfileSerializer(profile, data=request.data, partial=True, context={"facility": facility})
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        if profile.department_id:
            profile.user.unit = profile.department
            profile.user.unit_restricted = True
        profile.user.status = UserStatus.ACTIVE if profile.is_active else UserStatus.SUSPENDED
        profile.user.save(update_fields=["unit", "unit_restricted", "status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=request.user, target=profile, metadata={"event": "facility_staff_profile_updated"})
        return Response(FacilityStaffProfileSerializer(profile, context={"facility": facility}).data)

    @action(detail=True, methods=["patch"], url_path=r"staff/(?P<staff_profile_id>[^/.]+)/suspend")
    def suspend_staff(self, request, pk=None, staff_profile_id=None):
        if request.user.role != UserRole.FACILITY_ADMIN:
            raise PermissionDenied("Only facility admins can manage facility staff.")
        facility = self.get_object()
        profile = get_object_or_404(FacilityStaffProfile, id=staff_profile_id, facility=facility)
        profile.is_active = False
        profile.save(update_fields=["is_active", "updated_at"])
        profile.user.status = UserStatus.SUSPENDED
        profile.user.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=request.user, target=profile, metadata={"event": "facility_staff_suspended"})
        return Response(FacilityStaffProfileSerializer(profile, context={"facility": facility}).data)

    @action(detail=True, methods=["patch"], url_path=r"staff/(?P<staff_profile_id>[^/.]+)/reactivate")
    def reactivate_staff(self, request, pk=None, staff_profile_id=None):
        if request.user.role != UserRole.FACILITY_ADMIN:
            raise PermissionDenied("Only facility admins can manage facility staff.")
        facility = self.get_object()
        profile = get_object_or_404(FacilityStaffProfile, id=staff_profile_id, facility=facility)
        profile.is_active = True
        profile.save(update_fields=["is_active", "updated_at"])
        profile.user.status = UserStatus.ACTIVE
        profile.user.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=request.user, target=profile, metadata={"event": "facility_staff_reactivated"})
        return Response(FacilityStaffProfileSerializer(profile, context={"facility": facility}).data)

    @action(detail=True, methods=["get", "post"], url_path="invites")
    def invites(self, request, pk=None):
        if request.user.role != UserRole.FACILITY_ADMIN:
            raise PermissionDenied("Only facility admins can manage facility invites.")
        facility = self.get_object()
        if request.method == "GET":
            invites = UserInvite.objects.select_related("organization", "unit", "invited_by").filter(organization=facility.organization)
            return Response(FacilityInviteSerializer(invites, many=True).data)

        serializer = FacilityStaffInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        department = None
        department_id = serializer.validated_data.get("department")
        if department_id:
            department = get_object_or_404(OrganizationUnit, id=department_id, organization=facility.organization)
        invite = UserInvite.objects.create(
            organization=facility.organization,
            unit=department,
            invited_by=request.user,
            email=serializer.validated_data["email"],
            phone=serializer.validated_data.get("phone", ""),
            role=serializer.validated_data["role"],
            facility_staff_type=serializer.validated_data["staff_type"],
            message=serializer.validated_data.get("message", ""),
            token=secrets.token_urlsafe(32),
            expires_at=serializer.validated_data.get("expires_at") or timezone.now() + timedelta(days=7),
        )
        log_action(action=AuditAction.CREATE, actor=request.user, target=invite, metadata={"event": "facility_staff_invite_sent"})
        return Response(FacilityInviteSerializer(invite).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path=r"invites/(?P<invite_id>[^/.]+)")
    def revoke_invite(self, request, pk=None, invite_id=None):
        if request.user.role != UserRole.FACILITY_ADMIN:
            raise PermissionDenied("Only facility admins can manage facility invites.")
        facility = self.get_object()
        invite = get_object_or_404(UserInvite, id=invite_id, organization=facility.organization)
        invite.status = InviteStatus.REVOKED
        invite.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=request.user, target=invite, metadata={"event": "facility_staff_invite_revoked"})
        return Response(FacilityInviteSerializer(invite).data)

    @action(detail=True, methods=["get"], url_path="appointments")
    def appointments(self, request, pk=None):
        facility = self.get_object()
        appointments = Appointment.objects.select_related(
            "food_handler",
            "food_handler__user",
            "food_handler__employer",
            "facility",
            "facility__organization",
            "doctor",
        ).prefetch_related("assessments__payment_transaction").filter(facility=facility)
        return Response(AppointmentSerializer(appointments, many=True).data)

    @action(detail=True, methods=["patch"], url_path=r"appointments/(?P<appointment_id>[^/.]+)/confirm")
    def confirm_appointment(self, request, pk=None, appointment_id=None):
        facility = self.get_object()
        appointment = get_object_or_404(Appointment, id=appointment_id, facility=facility)
        serializer = AppointmentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AssessmentService.confirm_appointment(
            appointment=appointment,
            actor=request.user,
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=["patch"], url_path=r"appointments/(?P<appointment_id>[^/.]+)/reschedule")
    def reschedule_appointment(self, request, pk=None, appointment_id=None):
        facility = self.get_object()
        appointment = get_object_or_404(Appointment, id=appointment_id, facility=facility)
        serializer = AppointmentRescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AssessmentService.reschedule_appointment(
            appointment=appointment,
            actor=request.user,
            appointment_date=serializer.validated_data["appointment_date"],
            reason=serializer.validated_data.get("reason", ""),
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=["patch"], url_path=r"appointments/(?P<appointment_id>[^/.]+)/cancel")
    def cancel_appointment(self, request, pk=None, appointment_id=None):
        facility = self.get_object()
        appointment = get_object_or_404(Appointment, id=appointment_id, facility=facility)
        serializer = AppointmentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AssessmentService.cancel_appointment(
            appointment=appointment,
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=["patch"], url_path=r"appointments/(?P<appointment_id>[^/.]+)/no-show")
    def no_show_appointment(self, request, pk=None, appointment_id=None):
        facility = self.get_object()
        appointment = get_object_or_404(Appointment, id=appointment_id, facility=facility)
        serializer = AppointmentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AssessmentService.mark_appointment_no_show(
            appointment=appointment,
            actor=request.user,
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=["patch"], url_path=r"appointments/(?P<appointment_id>[^/.]+)/assign-doctor")
    def assign_appointment_doctor(self, request, pk=None, appointment_id=None):
        facility = self.get_object()
        appointment = get_object_or_404(Appointment, id=appointment_id, facility=facility)
        serializer = AppointmentAssignDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AssessmentService.assign_appointment_doctor(
            appointment=appointment,
            doctor=serializer.validated_data["doctor"],
            actor=request.user,
        )
        return Response(AppointmentSerializer(appointment).data)

    def _facility_assessment_queryset(self, facility):
        queryset = facility.assessments.select_related(
            "food_handler",
            "food_handler__business_branch",
            "employer",
            "facility",
            "doctor",
            "appointment",
            "payment_transaction",
        ).prefetch_related("lab_tests", "vaccinations").order_by("-created_at")
        params = self.request.query_params
        if params.get("status"):
            queryset = queryset.filter(status=params["status"])
        if params.get("doctor"):
            queryset = queryset.filter(doctor_id=params["doctor"])
        if params.get("lab_status"):
            queryset = queryset.filter(lab_status=params["lab_status"])
        if params.get("decision_status"):
            queryset = queryset.filter(final_decision=params["decision_status"])
        if params.get("assessment_type"):
            queryset = queryset.filter(assessment_type=params["assessment_type"])
        if params.get("queue") == "return-to-work":
            queryset = queryset.filter(assessment_type="return_to_work")
        if params.get("employer"):
            queryset = queryset.filter(employer_id=params["employer"])
        if params.get("branch"):
            queryset = queryset.filter(food_handler__business_branch_id=params["branch"])
        if params.get("payment_status"):
            if params["payment_status"] == "missing":
                queryset = queryset.filter(payment_transaction__isnull=True)
            else:
                queryset = queryset.filter(payment_transaction__status=params["payment_status"])
        if params.get("certificate_submission_status"):
            value = params["certificate_submission_status"]
            if value == "not_submitted":
                queryset = queryset.filter(certificate_request__isnull=True, certificate__isnull=True)
            elif value == "certificate_issued":
                queryset = queryset.filter(certificate__isnull=False)
            else:
                queryset = queryset.filter(certificate_request__status=value)
        if params.get("date_from"):
            queryset = queryset.filter(created_at__date__gte=params["date_from"])
        if params.get("date_to"):
            queryset = queryset.filter(created_at__date__lte=params["date_to"])
        return queryset

    @action(detail=True, methods=["get"], url_path="assessments")
    def assessments(self, request, pk=None):
        facility = self.get_object()
        return Response(FacilityAssessmentSerializer(self._facility_assessment_queryset(facility), many=True, context={"request": request}).data)

    @action(detail=True, methods=["get"], url_path=r"assessments/(?P<assessment_id>[^/.]+)")
    def assessment_detail(self, request, pk=None, assessment_id=None):
        facility = self.get_object()
        assessment = get_object_or_404(self._facility_assessment_queryset(facility), id=assessment_id)
        log_action(
            action=AuditAction.MEDICAL_RECORD_ACCESS,
            actor=request.user,
            target=assessment,
            request=request,
            metadata={"event": "facility_assessment_detail_read"},
        )
        return Response(FacilityAssessmentDetailSerializer(assessment, context={"request": request}).data)

    @action(detail=True, methods=["patch"], url_path=r"assessments/(?P<assessment_id>[^/.]+)/assign-doctor")
    def assign_assessment_doctor(self, request, pk=None, assessment_id=None):
        facility = self.get_object()
        assessment = get_object_or_404(self._facility_assessment_queryset(facility), id=assessment_id)
        serializer = AssessmentAssignDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = AssessmentService.assign_assessment_doctor(
            assessment=assessment,
            doctor=serializer.validated_data["doctor"],
            actor=request.user,
        )
        return Response(FacilityAssessmentSerializer(assessment, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path=r"assessments/(?P<assessment_id>[^/.]+)/submit-to-state")
    def submit_assessment_to_state(self, request, pk=None, assessment_id=None):
        facility = self.get_object()
        assessment = get_object_or_404(self._facility_assessment_queryset(facility), id=assessment_id)
        serializer = RequestCertificateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate_request = CertificateService.submit_to_state(
            assessment=assessment,
            actor=request.user,
            notes=serializer.validated_data.get("request_notes", ""),
        )
        return Response(CertificateRequestSerializer(certificate_request).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path=r"assessments/(?P<assessment_id>[^/.]+)/respond-to-clarification")
    def respond_assessment_clarification(self, request, pk=None, assessment_id=None):
        facility = self.get_object()
        assessment = get_object_or_404(self._facility_assessment_queryset(facility), id=assessment_id)
        serializer = CertificateClarificationResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate_request = getattr(assessment, "certificate_request", None)
        if not certificate_request:
            raise ValidationError("This assessment has not been submitted to State validation.")
        certificate_request = CertificateService.respond_to_clarification(
            certificate_request=certificate_request,
            actor=request.user,
            response=serializer.validated_data["response"],
        )
        return Response(CertificateRequestSerializer(certificate_request).data)


class FacilityAccreditationApplicationViewSet(viewsets.ModelViewSet):
    queryset = FacilityAccreditationApplication.objects.select_related(
        "facility",
        "facility__organization",
        "facility__state",
        "reviewer",
    ).order_by("-created_at")
    serializer_class = FacilityAccreditationApplicationSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        queryset = self.queryset
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return queryset.filter(facility__state=user.state)
        if user.organization_id:
            return queryset.filter(facility__organization=user.organization)
        return queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        facility = serializer.validated_data["facility"]
        if user.role != UserRole.FACILITY_ADMIN:
            raise PermissionDenied("Only facility admins can create accreditation applications.")
        if facility.organization_id != user.organization_id:
            raise PermissionDenied("You can only apply for your own facility.")
        if FacilityAccreditationApplication.objects.filter(
            facility=facility,
            application_status__in=[
                AccreditationStatus.DRAFT,
                AccreditationStatus.SUBMITTED,
                AccreditationStatus.UNDER_REVIEW,
                AccreditationStatus.MORE_INFORMATION_REQUIRED,
                AccreditationStatus.APPROVED,
            ],
        ).exists():
            raise ValidationError("This facility already has an active accreditation application.")
        application = serializer.save()
        log_action(action=AuditAction.CREATE, actor=user, target=application)

    def perform_update(self, serializer):
        application = self.get_object()
        user = self.request.user
        if user.role != UserRole.FACILITY_ADMIN or application.facility.organization_id != user.organization_id:
            raise PermissionDenied("Only the facility admin can update their draft application.")
        if application.application_status not in {AccreditationStatus.DRAFT, AccreditationStatus.MORE_INFORMATION_REQUIRED}:
            raise ValidationError("Only draft or more-information-required applications can be updated.")
        updated = serializer.save()
        log_action(action=AuditAction.UPDATE, actor=user, target=updated)

    def _ensure_state_reviewer(self, application):
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return
        if user.role == UserRole.STATE_ADMIN and application.facility.state_id == user.state_id:
            return
        raise PermissionDenied("You cannot review this facility accreditation.")

    @action(detail=True, methods=["patch"], url_path="submit")
    def submit(self, request, pk=None):
        application = self.get_object()
        if request.user.role != UserRole.FACILITY_ADMIN or application.facility.organization_id != request.user.organization_id:
            raise PermissionDenied("Only the facility admin can submit this application.")
        if not application.checklist_complete:
            raise ValidationError("Accreditation checklist is incomplete.")
        application = FacilityAccreditationService.submit(application=application, actor=request.user)
        return Response(FacilityAccreditationApplicationSerializer(application).data)

    @action(detail=True, methods=["patch"], url_path="approve")
    def approve(self, request, pk=None):
        application = self.get_object()
        self._ensure_state_reviewer(application)
        serializer = AccreditationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = FacilityAccreditationService.approve(
            application=application,
            reviewer=request.user,
            review_comment=serializer.validated_data.get("review_comment", ""),
        )
        return Response(FacilityAccreditationApplicationSerializer(application).data)

    @action(detail=True, methods=["patch"], url_path="reject")
    def reject(self, request, pk=None):
        application = self.get_object()
        self._ensure_state_reviewer(application)
        serializer = AccreditationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = FacilityAccreditationService.reject(
            application=application,
            reviewer=request.user,
            review_comment=serializer.validated_data.get("review_comment", ""),
        )
        return Response(FacilityAccreditationApplicationSerializer(application).data)

    @action(detail=True, methods=["patch"], url_path="request-more-information")
    def request_more_information(self, request, pk=None):
        application = self.get_object()
        self._ensure_state_reviewer(application)
        serializer = AccreditationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = FacilityAccreditationService.request_more_information(
            application=application,
            reviewer=request.user,
            review_comment=serializer.validated_data.get("review_comment", ""),
        )
        return Response(FacilityAccreditationApplicationSerializer(application).data)

    @action(detail=True, methods=["patch"], url_path="suspend")
    def suspend(self, request, pk=None):
        application = self.get_object()
        self._ensure_state_reviewer(application)
        serializer = AccreditationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = FacilityAccreditationService.suspend(
            application=application,
            reviewer=request.user,
            review_comment=serializer.validated_data.get("review_comment", ""),
        )
        return Response(FacilityAccreditationApplicationSerializer(application).data)

    @action(detail=True, methods=["patch"], url_path="reactivate")
    def reactivate(self, request, pk=None):
        application = self.get_object()
        self._ensure_state_reviewer(application)
        serializer = AccreditationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = FacilityAccreditationService.reactivate(
            application=application,
            reviewer=request.user,
            review_comment=serializer.validated_data.get("review_comment", ""),
        )
        return Response(FacilityAccreditationApplicationSerializer(application).data)


class FacilityDocumentViewSet(viewsets.ModelViewSet):
    queryset = FacilityDocument.objects.select_related(
        "facility",
        "facility__organization",
        "facility__state",
        "accreditation_application",
        "uploaded_by",
    ).order_by("-created_at")
    serializer_class = FacilityDocumentSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["facility", "accreditation_application", "document_type", "status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        queryset = self.queryset
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return queryset.filter(facility__state=user.state)
        if user.organization_id:
            return queryset.filter(facility__organization=user.organization)
        return queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        facility = serializer.validated_data["facility"]
        if user.role != UserRole.FACILITY_ADMIN:
            raise PermissionDenied("Only facility admins can upload accreditation documents.")
        if facility.organization_id != user.organization_id:
            raise PermissionDenied("You can only upload documents for your own facility.")
        document = serializer.save(uploaded_by=user)
        log_action(
            action=AuditAction.CREATE,
            actor=user,
            target=document,
            metadata={"event": "facility_document_uploaded", "document_type": document.document_type},
        )
