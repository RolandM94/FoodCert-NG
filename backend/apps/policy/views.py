from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.policy.models import StatePolicyConfig
from apps.policy.serializers import StatePolicyConfigSerializer


class StatePolicyConfigViewSet(viewsets.ModelViewSet):
    queryset = StatePolicyConfig.objects.select_related("state", "updated_by").order_by("state__name")
    serializer_class = StatePolicyConfigSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        if user.role == UserRole.STATE_ADMIN:
            return self.queryset.filter(state=user.state)
        return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != UserRole.FEDERAL_ADMIN and user.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Only federal admins can create state policy configuration.")
        config = serializer.save(updated_by=user)
        log_action(action=AuditAction.UPDATE, actor=user, target=config, metadata={"event": "state_policy_created"})

    def perform_update(self, serializer):
        user = self.request.user
        if user.role != UserRole.FEDERAL_ADMIN and user.role != UserRole.SUPER_ADMIN:
            raise PermissionDenied("Only federal admins can update state policy configuration.")
        config = serializer.save(updated_by=user)
        log_action(action=AuditAction.UPDATE, actor=user, target=config, metadata={"event": "state_policy_updated"})
