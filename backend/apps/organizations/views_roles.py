from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.organizations.models import Role, RolePermission
from apps.organizations.serializers_roles import (
    CreateRoleSerializer,
    PermissionSerializer,
    RoleDetailSerializer,
    RoleListSerializer,
    RolePermissionWriteSerializer,
    UpdateRoleSerializer,
)


class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        queryset = Role.objects.annotate(permission_count=Count("role_permissions", distinct=True)).order_by("organization_type", "name")
        organization_type = self.kwargs.get("organization_type") or self.request.query_params.get("organization_type")
        status_filter = self.request.query_params.get("status")
        search = self.request.query_params.get("search")
        if organization_type:
            queryset = queryset.filter(organization_type=organization_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if search:
            queryset = queryset.filter(name__icontains=search) | queryset.filter(code__icontains=search)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateRoleSerializer
        if self.action in {"partial_update", "update"}:
            return UpdateRoleSerializer
        if self.action in {"retrieve", "permissions"}:
            return RoleDetailSerializer
        return RoleListSerializer

    def create(self, request, *args, **kwargs):
        if request.user.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Only super admins can create custom roles.")
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        return Response(RoleDetailSerializer(self.get_queryset().get(pk=role.pk)).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        role = self.get_object()
        if request.user.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Only super admins can update roles.")
        if role.is_system_role and set(request.data.keys()) - {"status", "description"}:
            raise ValidationError("Only status and description can be updated on system roles.")
        serializer = self.get_serializer(role, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RoleDetailSerializer(self.get_queryset().get(pk=role.pk)).data)

    @action(detail=True, methods=["get", "post"], url_path="permissions")
    def permissions(self, request, pk=None):
        role = self.get_object()
        if request.method == "GET":
            permissions = role.role_permissions.select_related("permission").order_by("permission__module", "permission__code")
            return Response(PermissionSerializer([link.permission for link in permissions], many=True).data)

        if request.user.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Only super admins can modify role permissions.")
        if role.is_system_role:
            raise ValidationError("System role permissions cannot be modified here.")
        serializer = RolePermissionWriteSerializer(data=request.data, context={"role": role})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RoleDetailSerializer(self.get_queryset().get(pk=role.pk)).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path=r"permissions/(?P<permission_id>[^/.]+)")
    def remove_permission(self, request, pk=None, permission_id=None):
        role = self.get_object()
        if request.user.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Only super admins can modify role permissions.")
        if role.is_system_role:
            raise ValidationError("System role permissions cannot be modified here.")
        RolePermission.objects.filter(role=role, permission_id=permission_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
