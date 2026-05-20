from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.facilities.models import AccreditationStatus, FacilityAccreditationApplication, MedicalFacility
from apps.facilities.serializers import (
    AccreditationReviewSerializer,
    FacilityAccreditationApplicationSerializer,
    MedicalFacilitySerializer,
)
from apps.facilities.services import FacilityAccreditationService


class MedicalFacilityViewSet(viewsets.ModelViewSet):
    queryset = MedicalFacility.objects.select_related("organization", "state", "lga", "approved_by").order_by("-created_at")
    serializer_class = MedicalFacilitySerializer
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
        if application.application_status != AccreditationStatus.DRAFT:
            raise ValidationError("Only draft applications can be updated.")
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
