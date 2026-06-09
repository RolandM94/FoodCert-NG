from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import CanManageOrganization, IsActiveUser
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.organizations.models import Organization, OrganizationStatus, OrganizationUnit
from apps.organizations.permissions import CanManageOrganizationUnit
from apps.organizations.serializers import OrganizationSerializer, OrganizationUnitAssignUserSerializer, OrganizationUnitSerializer
from apps.organizations.services import archive_unit, assign_user_to_unit, create_unit, deactivate_unit, get_unit_tree, reactivate_unit, update_unit


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.select_related("parent", "state", "lga", "created_by").order_by("name")
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageOrganization]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        queryset = self.queryset
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            pass
        elif user.role == UserRole.STATE_ADMIN:
            queryset = queryset.filter(state=user.state)
        elif user.organization_id:
            queryset = queryset.filter(pk=user.organization_id)
        else:
            return queryset.none()
        if self.request.query_params.get("status"):
            queryset = queryset.filter(status=self.request.query_params["status"])
        if self.request.query_params.get("organization_type"):
            queryset = queryset.filter(organization_type=self.request.query_params["organization_type"])
        if self.request.query_params.get("state"):
            queryset = queryset.filter(state_id=self.request.query_params["state"])
        if user.role == UserRole.STATE_ADMIN:
            queryset = queryset.filter(state=user.state)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in {UserRole.SUPER_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("You cannot create organizations.")
        if user.role == UserRole.STATE_ADMIN and serializer.validated_data.get("state") != user.state:
            raise PermissionDenied("State admins can only create organizations in their state.")
        organization = serializer.save(created_by=user)
        log_action(action=AuditAction.CREATE, actor=self.request.user, target=organization)

    def perform_update(self, serializer):
        organization = serializer.save()
        log_action(action=AuditAction.UPDATE, actor=self.request.user, target=organization)

    @action(detail=True, methods=["post"], url_path="suspend")
    def suspend(self, request, pk=None):
        organization = self.get_object()
        organization.status = OrganizationStatus.SUSPENDED
        organization.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=request.user, target=organization, metadata={"event": "organization_suspended"})
        return Response(self.get_serializer(organization).data)

    @action(detail=True, methods=["post"], url_path="reactivate")
    def reactivate(self, request, pk=None):
        organization = self.get_object()
        if organization.status == OrganizationStatus.ARCHIVED:
            raise PermissionDenied("Archived organizations cannot be reactivated directly.")
        organization.status = OrganizationStatus.ACTIVE
        organization.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=request.user, target=organization, metadata={"event": "organization_reactivated"})
        return Response(self.get_serializer(organization).data)


class OrganizationUnitViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationUnitSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, CanManageOrganizationUnit]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_organization(self):
        return Organization.objects.get(id=self.kwargs["organization_id"])

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return OrganizationUnit.objects.select_related("organization", "parent", "manager", "state", "lga", "created_by").prefetch_related("children", "memberships", "members")
        organization_id = self.kwargs["organization_id"]
        queryset = OrganizationUnit.objects.select_related("organization", "parent", "manager", "state", "lga", "created_by").prefetch_related("children", "memberships", "members").filter(organization_id=organization_id)
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

    @action(detail=True, methods=["get"], url_path="members")
    def members(self, request, organization_id=None, pk=None):
        unit = self.get_object()
        direct_members = [
            {
                "id": str(user.id),
                "name": user.get_full_name() or user.username,
                "email": user.email,
                "role": user.role,
                "status": user.status,
                "unit_restricted": user.unit_restricted,
            }
            for user in unit.members.order_by("email")
        ]
        membership_members = [
            {
                "id": str(membership.user_id),
                "name": membership.user.get_full_name() or membership.user.username,
                "email": membership.user.email,
                "role": membership.role.code,
                "status": membership.status,
                "unit_restricted": membership.unit_restricted,
            }
            for membership in unit.memberships.select_related("user", "role").filter(status="active").order_by("user__email")
        ]
        seen = set()
        members = []
        for member in membership_members + direct_members:
            if member["id"] in seen:
                continue
            seen.add(member["id"])
            members.append(member)
        return Response(members)

    @action(detail=True, methods=["post"], url_path="assign-user")
    def assign_user(self, request, organization_id=None, pk=None):
        unit = self.get_object()
        serializer = OrganizationUnitAssignUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = assign_user_to_unit(
            actor=request.user,
            unit=unit,
            user=serializer.validated_data["user"],
            unit_restricted=serializer.validated_data["unit_restricted"],
        )
        return Response({"id": str(user.id), "unit": str(unit.id), "unit_restricted": user.unit_restricted})

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, organization_id=None, pk=None):
        unit = deactivate_unit(actor=request.user, unit=self.get_object())
        return Response(self.get_serializer(unit).data)

    @action(detail=True, methods=["post"], url_path="reactivate")
    def reactivate(self, request, organization_id=None, pk=None):
        unit = reactivate_unit(actor=request.user, unit=self.get_object())
        return Response(self.get_serializer(unit).data)

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, organization_id=None, pk=None):
        unit = archive_unit(actor=request.user, unit=self.get_object())
        return Response(self.get_serializer(unit).data)

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request, organization_id=None):
        return Response(get_unit_tree(self.get_organization()))
