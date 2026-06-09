from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsActiveUser
from apps.organizations.models import Permission
from apps.organizations.serializers_roles import PermissionSerializer


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        queryset = Permission.objects.order_by("module", "code")
        module = self.request.query_params.get("module")
        search = self.request.query_params.get("search")
        if module:
            queryset = queryset.filter(module=module)
        if search:
            queryset = queryset.filter(code__icontains=search) | queryset.filter(name__icontains=search) | queryset.filter(description__icontains=search)
        return queryset.distinct()
