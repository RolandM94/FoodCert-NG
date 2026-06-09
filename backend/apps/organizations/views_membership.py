from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.organizations.models import MembershipStatus, Organization, OrganizationMembership
from apps.organizations.serializers_membership import (
    ChangeRoleSerializer,
    ChangeUnitSerializer,
    CreateMembershipSerializer,
    MembershipDetailSerializer,
    MembershipListSerializer,
    UpdateMembershipSerializer,
)
from apps.organizations.services_membership import (
    change_role,
    change_unit,
    create_membership,
    reactivate_membership,
    remove_membership,
    suspend_membership,
    toggle_unit_restriction,
    update_membership,
)


class OrganizationMembershipViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_organization(self):
        return Organization.objects.get(id=self.kwargs["organization_id"])

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return OrganizationMembership.objects.select_related("user", "organization", "role", "unit")
        organization = self.get_organization()
        queryset = OrganizationMembership.objects.select_related("user", "organization", "role", "unit").filter(organization=organization)
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return queryset
        if user.role == UserRole.STATE_ADMIN:
            return queryset.filter(organization__state=user.state)
        if user.organization_id == organization.id:
            return queryset
        return queryset.none()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateMembershipSerializer
        if self.action in {"partial_update", "update"}:
            return UpdateMembershipSerializer
        if self.action == "change_role":
            return ChangeRoleSerializer
        if self.action == "change_unit":
            return ChangeUnitSerializer
        if self.action == "retrieve":
            return MembershipDetailSerializer
        return MembershipListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = create_membership(
            actor=request.user,
            organization=self.get_organization(),
            user=serializer.validated_data["user"],
            role=serializer.validated_data["role"],
            unit=serializer.validated_data.get("unit"),
            unit_restricted=serializer.validated_data["unit_restricted"],
        )
        return Response(MembershipDetailSerializer(membership).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        membership = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        membership = update_membership(
            actor=request.user,
            membership=membership,
            role=serializer.validated_data.get("role"),
            unit=serializer.validated_data.get("unit") if "unit" in serializer.validated_data else None,
            unit_restricted=serializer.validated_data.get("unit_restricted") if "unit_restricted" in serializer.validated_data else None,
        )
        return Response(MembershipDetailSerializer(membership).data)

    @action(detail=True, methods=["patch"], url_path="suspend")
    def suspend(self, request, organization_id=None, pk=None):
        return Response(MembershipDetailSerializer(suspend_membership(actor=request.user, membership=self.get_object())).data)

    @action(detail=True, methods=["patch"], url_path="reactivate")
    def reactivate(self, request, organization_id=None, pk=None):
        return Response(MembershipDetailSerializer(reactivate_membership(actor=request.user, membership=self.get_object())).data)

    @action(detail=True, methods=["patch"], url_path="remove")
    def remove(self, request, organization_id=None, pk=None):
        return Response(MembershipDetailSerializer(remove_membership(actor=request.user, membership=self.get_object())).data)

    @action(detail=True, methods=["patch"], url_path="change-role")
    def change_role(self, request, organization_id=None, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = change_role(actor=request.user, membership=self.get_object(), role=serializer.validated_data["role"])
        return Response(MembershipDetailSerializer(membership).data)

    @action(detail=True, methods=["patch"], url_path="change-unit")
    def change_unit(self, request, organization_id=None, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = change_unit(
            actor=request.user,
            membership=self.get_object(),
            unit=serializer.validated_data.get("unit"),
            unit_restricted=serializer.validated_data["unit_restricted"],
        )
        return Response(MembershipDetailSerializer(membership).data)

    @action(detail=True, methods=["patch"], url_path="toggle-unit-restriction")
    def toggle_unit_restriction(self, request, organization_id=None, pk=None):
        return Response(MembershipDetailSerializer(toggle_unit_restriction(actor=request.user, membership=self.get_object())).data)
