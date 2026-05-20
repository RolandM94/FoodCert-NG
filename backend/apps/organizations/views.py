from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import CanManageOrganization, IsActiveUser
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.organizations.models import Organization, OrganizationUnit
from apps.organizations.permissions import CanManageOrganizationUnit
from apps.organizations.serializers import OrganizationSerializer, OrganizationUnitSerializer
from apps.organizations.services import create_unit, deactivate_unit, ensure_can_manage_units, update_unit


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.select_related("state", "lga").order_by("name")
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageOrganization]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        queryset = self.queryset
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return queryset
        if user.role == UserRole.STATE_ADMIN:
            return queryset.filter(state=user.state)
        if user.organization_id:
            return queryset.filter(pk=user.organization_id)
        return queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in {UserRole.SUPER_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("You cannot create organizations.")
        if user.role == UserRole.STATE_ADMIN and serializer.validated_data.get("state") != user.state:
            raise PermissionDenied("State admins can only create organizations in their state.")
        organization = serializer.save()
        log_action(action=AuditAction.CREATE, actor=self.request.user, target=organization)

    def perform_update(self, serializer):
        organization = serializer.save()
        log_action(action=AuditAction.UPDATE, actor=self.request.user, target=organization)


class OrganizationUnitViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationUnitSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageOrganizationUnit]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_organization(self):
        return Organization.objects.get(id=self.kwargs["organization_id"])

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return OrganizationUnit.objects.select_related("organization", "parent", "state", "lga")
        organization_id = self.kwargs["organization_id"]
        queryset = OrganizationUnit.objects.select_related("organization", "parent", "state", "lga").filter(organization_id=organization_id)
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return queryset
        if user.role == UserRole.STATE_ADMIN:
            return queryset.filter(organization__state=user.state)
        if user.organization_id == organization_id:
            return queryset
        return queryset.none()

    def perform_create(self, serializer):
        organization = self.get_organization()
        unit = create_unit(
            actor=self.request.user,
            organization=organization,
            **serializer.validated_data,
        )
        serializer.instance = unit

    def perform_update(self, serializer):
        unit = update_unit(
            actor=self.request.user,
            unit=serializer.instance,
            **serializer.validated_data,
        )
        serializer.instance = unit

    def destroy(self, request, *args, **kwargs):
        unit = self.get_object()
        deactivate_unit(actor=request.user, unit=unit)
        return Response(status=status.HTTP_204_NO_CONTENT)
