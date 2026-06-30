import json
import secrets
from datetime import timedelta

from django.db.models import Count, Max, Q
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
    AssessmentAssignLabSerializer,
    AssessmentCheckInSerializer,
    AssessmentIdentityMismatchSerializer,
    AppointmentAssignDoctorSerializer,
    AppointmentDetailSerializer,
    FacilityPaymentConfirmationSerializer,
    AppointmentRescheduleSerializer,
    AppointmentSerializer,
    AppointmentTransitionSerializer,
    FacilityAssessmentDetailSerializer,
    FacilityAssessmentSerializer,
)
from apps.audit.models import AuditLog
from apps.assessments.services import AssessmentService
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.certificates.serializers import CertificateClarificationResponseSerializer, CertificateRequestSerializer, RequestCertificateSerializer
from apps.certificates.services import CertificateService
from apps.facilities.models import (
    AccreditationStatus,
    FacilityAccreditationApplication,
    FacilityDocument,
    FacilityInvitation,
    FacilityProfessionalProfile,
    FacilityRole,
    FacilityStaffProfile,
    FacilityTeamMemberStatus,
    MedicalFacility,
)
from apps.facilities.serializers import (
    AccreditationReviewSerializer,
    FacilityAccreditationApplicationSerializer,
    FacilityTemporaryUnfitReportSerializer,
    FacilityDocumentSerializer,
    FacilityInviteSerializer,
    FacilityRoleSerializer,
    FacilityRoleWriteSerializer,
    FacilityAuditLogSerializer,
    FacilityStaffInviteSerializer,
    FacilityStaffProfileSerializer,
    FacilityStaffUpdateSerializer,
    FacilityTeamInvitationSerializer,
    MedicalFacilitySerializer,
)
from apps.facilities.services import FacilityAccreditationService, FacilityProfileService, FacilityTeamService
from apps.organizations.models import OrganizationUnit
from apps.organizations.models import OrganizationUnitType
from apps.organizations.serializers import OrganizationUnitSerializer
from apps.organizations.services import create_unit, deactivate_unit, update_unit
from apps.payments.permissions import ensure_facility_payment_confirmation_access
from apps.payments.services import PaymentService
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
        facility = FacilityProfileService.get_facility_membership_for_user(user)
        if facility:
            return queryset.filter(id=facility.id)
        return queryset.none()

    def _ensure_facility_membership(self, facility):
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR} and facility.state_id == user.state_id:
            return
        member_facility = FacilityProfileService.get_facility_membership_for_user(user)
        if not member_facility or member_facility.id != facility.id:
            raise PermissionDenied("You do not belong to this medical facility.")

    def _ensure_facility_permission(self, facility, *permission_keys, any_of=False):
        self._ensure_facility_membership(facility)
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return
        checks = [
            FacilityTeamService.has_permission(user=user, facility=facility, permission_key=permission_key)
            for permission_key in permission_keys
        ]
        allowed = any(checks) if any_of else all(checks)
        if not allowed:
            if len(permission_keys) == 1:
                raise PermissionDenied(f"You do not have the required facility permission: {permission_keys[0]}.")
            raise PermissionDenied("You do not have the required facility permissions for this action.")

    def _ensure_facility_admin_control(self, facility, *, required_permission=None):
        self._ensure_facility_membership(facility)
        if self.request.user.role != UserRole.FACILITY_ADMIN:
            raise PermissionDenied("Only facility admins can perform this action.")
        if required_permission:
            self._ensure_facility_permission(facility, required_permission)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != UserRole.FACILITY_ADMIN:
            raise PermissionDenied("Only facility admins can register a medical facility.")
        if MedicalFacility.objects.filter(organization=user.organization).exists():
            raise ValidationError("This organization already has a medical facility.")
        facility = serializer.save(organization=user.organization, state=user.state or serializer.validated_data["state"])
        FacilityTeamService.ensure_default_roles(facility=facility, actor=user)
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
        if request.method == "GET":
            facility = None
            if request.user.role == UserRole.FACILITY_ADMIN:
                facility = FacilityProfileService.get_for_user(request.user)
            else:
                staff_profile = getattr(request.user, "facility_staff_profile", None)
                if staff_profile and staff_profile.is_active and staff_profile.status == FacilityTeamMemberStatus.ACTIVE:
                    facility = staff_profile.facility
            if not facility:
                raise PermissionDenied("Only active facility admins or facility team members can access the current facility profile.")
            return Response(MedicalFacilitySerializer(facility).data)
        if request.user.role != UserRole.FACILITY_ADMIN:
            raise PermissionDenied("Only facility admins can update the current facility profile.")
        facility = FacilityProfileService.get_for_user(request.user)
        if not facility:
            raise ValidationError("No medical facility profile exists for this organization.")

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
        self._ensure_facility_membership(facility)
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

    @action(detail=True, methods=["get"], url_path="compliance-dashboard")
    def compliance_dashboard(self, request, pk=None):
        facility = self.get_object()
        self._ensure_facility_permission(facility, "compliance.view_dashboard")
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
        organization_logs = AuditLog.objects.filter(
            Q(organization=facility.organization) | Q(metadata__facility_id=str(facility.id))
        )
        if serializer.validated_data.get("date_from"):
            organization_logs = organization_logs.filter(created_at__date__gte=serializer.validated_data["date_from"])
        if serializer.validated_data.get("date_to"):
            organization_logs = organization_logs.filter(created_at__date__lte=serializer.validated_data["date_to"])
        payload.setdefault("sections", {})
        payload["sections"]["staff_activity"] = list(
            organization_logs.filter(actor__isnull=False)
            .values("actor_id", "actor__email", "actor__first_name", "actor__last_name", "actor__facility_staff_profile__role__name")
            .annotate(total_actions=Count("id"), last_activity=Max("created_at"))
            .order_by("-last_activity")[:8]
        )
        warnings = []
        accreditation_status = payload.get("cards", {}).get("accreditation_status")
        countdown = payload.get("cards", {}).get("reaccreditation_countdown_days")
        if accreditation_status in {AccreditationStatus.SUSPENDED, AccreditationStatus.EXPIRED}:
            warnings.append(
                {
                    "code": "accreditation_status",
                    "status": accreditation_status,
                    "message": f"Facility accreditation is {str(accreditation_status).replace('_', ' ')}.",
                }
            )
        if isinstance(countdown, int) and countdown <= 30:
            warnings.append(
                {
                    "code": "accreditation_expiry",
                    "status": "warning",
                    "message": f"Accreditation expires in {countdown} day{'s' if countdown != 1 else ''}.",
                }
            )
        payload["sections"]["warnings"] = warnings
        return Response(payload)

    @action(detail=True, methods=["get"], url_path="audit-logs")
    def audit_logs(self, request, pk=None):
        facility = self.get_object()
        self._ensure_facility_permission(facility, "audit_logs.view")
        queryset = AuditLog.objects.select_related("actor", "organization", "state").filter(
            Q(organization=facility.organization) | Q(metadata__facility_id=str(facility.id))
        ).order_by("-created_at")
        actor = request.query_params.get("actor", "").strip()
        role = request.query_params.get("role", "").strip()
        action = request.query_params.get("action", "").strip()
        assessment_id = request.query_params.get("assessment_id", "").strip()
        date_from = request.query_params.get("date_from", "").strip()
        date_to = request.query_params.get("date_to", "").strip()
        entity_type = request.query_params.get("entity_type", "").strip()
        if actor:
            queryset = queryset.filter(
                Q(actor__email__icontains=actor)
                | Q(actor__first_name__icontains=actor)
                | Q(actor__last_name__icontains=actor)
            )
        if role:
            queryset = queryset.filter(
                Q(actor__facility_staff_profile__role__name__icontains=role)
                | Q(actor__role__icontains=role)
            )
        if action:
            queryset = queryset.filter(action=action)
        if assessment_id:
            queryset = queryset.filter(
                Q(target_id__icontains=assessment_id)
                | Q(metadata__assessment_id=assessment_id)
            )
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        if entity_type:
            queryset = queryset.filter(target_type__iexact=entity_type)
        return Response(FacilityAuditLogSerializer(queryset[:200], many=True).data)

    @action(detail=True, methods=["get"], url_path="reports/performance")
    def performance_report(self, request, pk=None):
        facility = self.get_object()
        self._ensure_facility_membership(facility)
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
        self._ensure_facility_admin_control(facility, required_permission="facility.profile.edit")
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
        self._ensure_facility_admin_control(facility, required_permission="facility.profile.edit")
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
        self._ensure_facility_admin_control(facility, required_permission="facility.profile.edit")
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
        facility = self.get_object()
        self._ensure_facility_admin_control(facility, required_permission="facility.team.invite")
        profiles = FacilityStaffProfile.objects.select_related("user", "facility", "department", "role", "invited_by").filter(facility=facility)
        return Response(FacilityStaffProfileSerializer(profiles, many=True, context={"facility": facility}).data)

    @action(detail=True, methods=["patch"], url_path=r"staff/(?P<staff_profile_id>[^/.]+)")
    def staff_detail(self, request, pk=None, staff_profile_id=None):
        facility = self.get_object()
        self._ensure_facility_admin_control(facility, required_permission="facility.team.invite")
        profile = get_object_or_404(
            FacilityStaffProfile.objects.select_related("user", "facility", "department", "role", "invited_by"),
            id=staff_profile_id,
            facility=facility,
        )
        serializer = FacilityStaffUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if "role" in serializer.validated_data:
            profile.role = get_object_or_404(FacilityRole, id=serializer.validated_data["role"], facility=facility)
        if "department" in serializer.validated_data:
            department_id = serializer.validated_data["department"]
            profile.department = get_object_or_404(OrganizationUnit, id=department_id, organization=facility.organization) if department_id else None
        for field in ["professional_category", "status", "professional_registration_number", "digital_signature_url", "is_active"]:
            if field in serializer.validated_data:
                setattr(profile, field, serializer.validated_data[field])
        if profile.status == FacilityTeamMemberStatus.ACTIVE and not profile.accepted_at:
            profile.accepted_at = timezone.now()
        update_fields = [
            "role",
            "department",
            "professional_category",
            "status",
            "professional_registration_number",
            "digital_signature_url",
            "is_active",
            "accepted_at",
            "updated_at",
        ]
        profile.save(update_fields=update_fields)
        if profile.department_id:
            profile.user.unit = profile.department
            profile.user.unit_restricted = True
        else:
            profile.user.unit = None
            profile.user.unit_restricted = False
        profile.user.status = UserStatus.ACTIVE if profile.is_active else UserStatus.SUSPENDED
        profile.user.save(update_fields=["unit", "unit_restricted", "status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=request.user, target=profile, metadata={"event": "facility_staff_profile_updated"})
        return Response(FacilityStaffProfileSerializer(profile, context={"facility": facility}).data)

    @action(detail=True, methods=["patch"], url_path=r"staff/(?P<staff_profile_id>[^/.]+)/suspend")
    def suspend_staff(self, request, pk=None, staff_profile_id=None):
        facility = self.get_object()
        self._ensure_facility_admin_control(facility, required_permission="facility.team.remove")
        profile = get_object_or_404(FacilityStaffProfile, id=staff_profile_id, facility=facility)
        profile.is_active = False
        profile.save(update_fields=["is_active", "updated_at"])
        profile.user.status = UserStatus.SUSPENDED
        profile.user.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=request.user, target=profile, metadata={"event": "facility_staff_suspended"})
        return Response(FacilityStaffProfileSerializer(profile, context={"facility": facility}).data)

    @action(detail=True, methods=["patch"], url_path=r"staff/(?P<staff_profile_id>[^/.]+)/reactivate")
    def reactivate_staff(self, request, pk=None, staff_profile_id=None):
        facility = self.get_object()
        self._ensure_facility_admin_control(facility, required_permission="facility.team.remove")
        profile = get_object_or_404(FacilityStaffProfile, id=staff_profile_id, facility=facility)
        profile.is_active = True
        profile.save(update_fields=["is_active", "updated_at"])
        profile.user.status = UserStatus.ACTIVE
        profile.user.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=request.user, target=profile, metadata={"event": "facility_staff_reactivated"})
        return Response(FacilityStaffProfileSerializer(profile, context={"facility": facility}).data)

    @action(detail=True, methods=["get", "post"], url_path="invites")
    def invites(self, request, pk=None):
        facility = self.get_object()
        self._ensure_facility_admin_control(facility, required_permission="facility.team.invite")
        if request.method == "GET":
            invites = FacilityInvitation.objects.select_related("invite", "role").filter(facility=facility)
            return Response(FacilityTeamInvitationSerializer(invites, many=True).data)

        serializer = FacilityStaffInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        department = None
        department_id = serializer.validated_data.get("department")
        if department_id:
            department = get_object_or_404(OrganizationUnit, id=department_id, organization=facility.organization)
        facility_role = None
        facility_role_id = serializer.validated_data.get("facility_role")
        if facility_role_id:
            facility_role = get_object_or_404(FacilityRole, id=facility_role_id, facility=facility)
        professional_category = serializer.validated_data["professional_category"]
        if facility_role:
            try:
                FacilityTeamService.validate_permission_assignment(
                    professional_category=professional_category,
                    permission_keys=list(
                        facility_role.permissions.filter(allowed=True).values_list("permission_key", flat=True)
                    ),
                )
            except ValueError as exc:
                raise ValidationError(exc.args[0])
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
        facility_invitation = FacilityInvitation.objects.create(
            facility=facility,
            invite=invite,
            role=facility_role,
            professional_category=professional_category,
            status=FacilityTeamMemberStatus.INVITED,
        )
        log_action(action=AuditAction.CREATE, actor=request.user, target=invite, metadata={"event": "facility_staff_invite_sent"})
        return Response(FacilityTeamInvitationSerializer(facility_invitation).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path=r"invites/(?P<invite_id>[^/.]+)")
    def revoke_invite(self, request, pk=None, invite_id=None):
        facility = self.get_object()
        self._ensure_facility_admin_control(facility, required_permission="facility.team.remove")
        invite = get_object_or_404(UserInvite, id=invite_id, organization=facility.organization)
        invite.status = InviteStatus.REVOKED
        invite.save(update_fields=["status", "updated_at"])
        FacilityInvitation.objects.filter(invite=invite, facility=facility).update(
            status=FacilityTeamMemberStatus.REMOVED,
            updated_at=timezone.now(),
        )
        log_action(action=AuditAction.UPDATE, actor=request.user, target=invite, metadata={"event": "facility_staff_invite_revoked"})
        facility_invite = FacilityInvitation.objects.select_related("invite", "role").get(invite=invite, facility=facility)
        return Response(FacilityTeamInvitationSerializer(facility_invite).data)

    @action(detail=True, methods=["get", "post"], url_path="roles")
    def roles(self, request, pk=None):
        facility = self.get_object()
        self._ensure_facility_admin_control(
            facility,
            required_permission="facility.roles.create" if request.method == "POST" else "facility.roles.edit",
        )
        if request.method == "GET":
            roles = FacilityRole.objects.prefetch_related("permissions").filter(facility=facility).order_by("is_system_default", "name")
            return Response(FacilityRoleSerializer(roles, many=True).data)

        serializer = FacilityRoleWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permission_keys = serializer.validated_data.get("permission_keys", [])
        try:
            FacilityTeamService.validate_permission_assignment(
                professional_category=serializer.validated_data["professional_category"],
                permission_keys=permission_keys,
            )
        except ValueError as exc:
            raise ValidationError(exc.args[0])
        role = FacilityRole.objects.create(
            facility=facility,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
            professional_category=serializer.validated_data["professional_category"],
            is_system_default=False,
            is_custom=True,
            created_by=request.user,
        )
        for permission_key in permission_keys:
            role.permissions.create(permission_key=permission_key, allowed=True)
        log_action(action=AuditAction.CREATE, actor=request.user, target=role, metadata={"event": "facility_role_created"})
        return Response(FacilityRoleSerializer(role).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "patch"], url_path=r"roles/(?P<role_id>[^/.]+)")
    def role_detail(self, request, pk=None, role_id=None):
        facility = self.get_object()
        self._ensure_facility_admin_control(
            facility,
            required_permission="facility.roles.assign_permissions" if request.method == "PATCH" else "facility.roles.edit",
        )
        role = get_object_or_404(FacilityRole.objects.prefetch_related("permissions"), id=role_id, facility=facility)
        if request.method == "GET":
            return Response(FacilityRoleSerializer(role).data)

        serializer = FacilityRoleWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        permission_keys = serializer.validated_data.get(
            "permission_keys",
            list(role.permissions.filter(allowed=True).values_list("permission_key", flat=True)),
        )
        professional_category = serializer.validated_data.get("professional_category", role.professional_category)
        try:
            FacilityTeamService.validate_permission_assignment(
                professional_category=professional_category,
                permission_keys=permission_keys,
            )
        except ValueError as exc:
            raise ValidationError(exc.args[0])
        for field in ["name", "description", "professional_category"]:
            if field in serializer.validated_data:
                setattr(role, field, serializer.validated_data[field])
        role.save(update_fields=["name", "description", "professional_category", "updated_at"])
        if "permission_keys" in serializer.validated_data:
            role.permissions.exclude(permission_key__in=permission_keys).delete()
            for permission_key in permission_keys:
                role.permissions.update_or_create(permission_key=permission_key, defaults={"allowed": True})
        log_action(action=AuditAction.UPDATE, actor=request.user, target=role, metadata={"event": "facility_role_updated"})
        return Response(FacilityRoleSerializer(role).data)

    @action(detail=True, methods=["get"], url_path="appointments")
    def appointments(self, request, pk=None):
        facility = self.get_object()
        self._ensure_facility_permission(facility, "appointments.view")
        appointments = Appointment.objects.select_related(
            "food_handler",
            "food_handler__user",
            "food_handler__employer",
            "facility",
            "facility__organization",
            "doctor",
        ).prefetch_related("assessments__payment_transaction").filter(facility=facility)
        return Response(AppointmentSerializer(appointments, many=True).data)

    @action(detail=True, methods=["get"], url_path=r"appointments/(?P<appointment_id>[^/.]+)")
    def appointment_detail(self, request, pk=None, appointment_id=None):
        facility = self.get_object()
        self._ensure_facility_permission(facility, "appointments.view")
        appointment = get_object_or_404(
            Appointment.objects.select_related(
                "food_handler",
                "food_handler__user",
                "food_handler__employer",
                "facility",
                "facility__organization",
                "doctor",
            ).prefetch_related("assessments__payment_transaction"),
            id=appointment_id,
            facility=facility,
        )
        return Response(AppointmentDetailSerializer(appointment).data)

    @action(detail=True, methods=["patch"], url_path=r"appointments/(?P<appointment_id>[^/.]+)/confirm")
    def confirm_appointment(self, request, pk=None, appointment_id=None):
        facility = self.get_object()
        self._ensure_facility_permission(facility, "appointments.confirm")
        appointment = get_object_or_404(Appointment, id=appointment_id, facility=facility)
        serializer = AppointmentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AssessmentService.confirm_appointment(
            appointment=appointment,
            actor=request.user,
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=["patch"], url_path=r"appointments/(?P<appointment_id>[^/.]+)/confirm-payment")
    def confirm_appointment_payment(self, request, pk=None, appointment_id=None):
        facility = self.get_object()
        self._ensure_facility_membership(facility)
        ensure_facility_payment_confirmation_access(request.user, facility)
        appointment = get_object_or_404(
            Appointment.objects.prefetch_related("assessments__payment_transaction__receipt"),
            id=appointment_id,
            facility=facility,
        )
        serializer = FacilityPaymentConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = appointment.assessments.select_related("payment_transaction").first()
        if not assessment or not assessment.payment_transaction_id:
            raise ValidationError("No payment transaction exists for this appointment.")
        try:
            PaymentService.confirm_payment_at_facility(
                transaction_obj=assessment.payment_transaction,
                actor=request.user,
                facility=facility,
                notes=serializer.validated_data.get("notes", ""),
                payment_method=serializer.validated_data.get("payment_method", "cash"),
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        appointment = get_object_or_404(
            Appointment.objects.select_related(
                "food_handler",
                "food_handler__user",
                "food_handler__employer",
                "facility",
                "facility__organization",
                "doctor",
            ).prefetch_related("assessments__payment_transaction__receipt"),
            id=appointment_id,
            facility=facility,
        )
        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=["patch"], url_path=r"appointments/(?P<appointment_id>[^/.]+)/reschedule")
    def reschedule_appointment(self, request, pk=None, appointment_id=None):
        facility = self.get_object()
        self._ensure_facility_permission(facility, "appointments.confirm")
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
        self._ensure_facility_permission(facility, "appointments.cancel")
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
        self._ensure_facility_permission(facility, "appointments.confirm")
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
        self._ensure_facility_permission(facility, "appointments.confirm")
        appointment = get_object_or_404(Appointment, id=appointment_id, facility=facility)
        serializer = AppointmentAssignDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AssessmentService.assign_appointment_doctor(
            appointment=appointment,
            doctor=serializer.validated_data["doctor"],
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(AppointmentSerializer(appointment).data)

    def _facility_assessment_queryset(self, facility):
        queryset = facility.assessments.select_related(
            "food_handler",
            "food_handler__business_branch",
            "employer",
            "facility",
            "doctor",
            "assigned_lab_staff",
            "assigned_lab_unit",
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
        self._ensure_facility_permission(
            facility,
            "appointments.view",
            "declaration.view",
            "lab_requests.view",
            any_of=True,
        )
        return Response(FacilityAssessmentSerializer(self._facility_assessment_queryset(facility), many=True, context={"request": request}).data)

    @action(detail=True, methods=["get"], url_path="temporary-unfit-reports")
    def temporary_unfit_reports(self, request, pk=None):
        facility = self.get_object()
        self._ensure_facility_permission(facility, "unfit_reports.view")
        assessments = self._facility_assessment_queryset(facility).filter(final_decision="temporarily_not_fit")
        report_index = {
            str(report.filters.get("assessment_id")): report
            for report in ReportService.generated_reports_queryset(request.user).filter(
                report_type=ReportType.TEMPORARILY_NOT_FIT
            )
        }
        rows = [
            {
                "assessment_id": assessment.id,
                "food_handler_name": assessment.food_handler.full_name,
                "employer_name": assessment.employer.business_name if assessment.employer_id else "",
                "status": assessment.food_handler.current_status,
                "final_decision": assessment.final_decision,
                "return_to_work_date": assessment.return_to_work_date.isoformat() if assessment.return_to_work_date else "",
                "signed_at": assessment.signed_at.isoformat() if assessment.signed_at else "",
                "report_id": getattr(report_index.get(str(assessment.id)), "id", None),
                "report_status": getattr(report_index.get(str(assessment.id)), "status", ""),
            }
            for assessment in assessments
        ]
        return Response(FacilityTemporaryUnfitReportSerializer(rows, many=True).data)

    @action(detail=True, methods=["get"], url_path=r"assessments/(?P<assessment_id>[^/.]+)")
    def assessment_detail(self, request, pk=None, assessment_id=None):
        facility = self.get_object()
        self._ensure_facility_permission(
            facility,
            "appointments.view",
            "declaration.view",
            "lab_requests.view",
            any_of=True,
        )
        assessment = get_object_or_404(self._facility_assessment_queryset(facility), id=assessment_id)
        log_action(
            action=AuditAction.MEDICAL_RECORD_ACCESS,
            actor=request.user,
            target=assessment,
            request=request,
            metadata={"event": "facility_assessment_detail_read"},
        )
        return Response(FacilityAssessmentDetailSerializer(assessment, context={"request": request}).data)

    @action(detail=True, methods=["patch"], url_path=r"assessments/(?P<assessment_id>[^/.]+)/check-in")
    def check_in_assessment(self, request, pk=None, assessment_id=None):
        facility = self.get_object()
        self._ensure_facility_permission(facility, "assessment.check_in", "assessment.verify_identity")
        assessment = get_object_or_404(self._facility_assessment_queryset(facility), id=assessment_id)
        serializer = AssessmentCheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = AssessmentService.check_in_assessment(
            assessment=assessment,
            actor=request.user,
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(FacilityAssessmentSerializer(assessment, context={"request": request}).data)

    @action(detail=True, methods=["patch"], url_path=r"assessments/(?P<assessment_id>[^/.]+)/flag-identity-mismatch")
    def flag_identity_mismatch(self, request, pk=None, assessment_id=None):
        facility = self.get_object()
        self._ensure_facility_permission(facility, "assessment.check_in", "assessment.verify_identity")
        assessment = get_object_or_404(self._facility_assessment_queryset(facility), id=assessment_id)
        serializer = AssessmentIdentityMismatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = AssessmentService.flag_identity_mismatch(
            assessment=assessment,
            actor=request.user,
            reason=serializer.validated_data["reason"],
        )
        return Response(FacilityAssessmentSerializer(assessment, context={"request": request}).data)

    @action(detail=True, methods=["patch"], url_path=r"assessments/(?P<assessment_id>[^/.]+)/assign-doctor")
    def assign_assessment_doctor(self, request, pk=None, assessment_id=None):
        facility = self.get_object()
        self._ensure_facility_permission(facility, "appointments.confirm")
        assessment = get_object_or_404(self._facility_assessment_queryset(facility), id=assessment_id)
        serializer = AssessmentAssignDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = AssessmentService.assign_assessment_doctor(
            assessment=assessment,
            doctor=serializer.validated_data["doctor"],
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(FacilityAssessmentSerializer(assessment, context={"request": request}).data)

    @action(detail=True, methods=["patch"], url_path=r"assessments/(?P<assessment_id>[^/.]+)/assign-lab")
    def assign_assessment_lab(self, request, pk=None, assessment_id=None):
        facility = self.get_object()
        self._ensure_facility_permission(facility, "lab_requests.view")
        assessment = get_object_or_404(self._facility_assessment_queryset(facility), id=assessment_id)
        serializer = AssessmentAssignLabSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lab_unit = None
        if serializer.validated_data.get("lab_unit"):
            lab_unit = get_object_or_404(
                OrganizationUnit,
                id=serializer.validated_data["lab_unit"],
                organization=facility.organization,
                unit_type=OrganizationUnitType.LAB_DEPARTMENT,
            )
        assessment = AssessmentService.assign_assessment_lab(
            assessment=assessment,
            actor=request.user,
            lab_staff=serializer.validated_data.get("lab_staff"),
            lab_unit=lab_unit,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(FacilityAssessmentSerializer(assessment, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path=r"assessments/(?P<assessment_id>[^/.]+)/submit-to-state")
    def submit_assessment_to_state(self, request, pk=None, assessment_id=None):
        facility = self.get_object()
        self._ensure_facility_permission(facility, "certificates.view")
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
        self._ensure_facility_permission(facility, "certificates.view")
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
