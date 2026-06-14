from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.audit.models import AuditAction, AuditLog
from apps.audit.services import log_action
from apps.policy.models import StatePolicyConfig
from apps.policy.serializers import StateAuditLogSerializer, StatePolicyConfigSerializer


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

    @action(detail=False, methods=["get", "patch"], url_path="my-medical-facility-settings")
    def my_medical_facility_settings(self, request):
        user = request.user
        if user.role != UserRole.STATE_ADMIN:
            raise PermissionDenied("Only state admins can manage medical facility accreditation settings.")
        if not user.state_id:
            raise PermissionDenied("State admin account is not linked to a state.")

        config, _ = StatePolicyConfig.objects.get_or_create(state=user.state)
        if request.method == "GET":
            return Response(StatePolicyConfigSerializer(config).data)

        serializer = StatePolicyConfigSerializer(
            config,
            data={"medical_facility_settings": request.data.get("medical_facility_settings", request.data)},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user)
        log_action(
            action=AuditAction.UPDATE,
            actor=user,
            target=config,
            metadata={"event": "state_medical_facility_settings_updated"},
        )
        return Response(serializer.data)

    def _current_state_config(self, request):
        user = request.user
        if user.role != UserRole.STATE_ADMIN:
            raise PermissionDenied("Only state admins can manage state account settings.")
        if not user.state_id:
            raise PermissionDenied("State admin account is not linked to a state.")
        config, _ = StatePolicyConfig.objects.get_or_create(state=user.state)
        return config

    def _settings_action(self, request, *, field_name, event_name):
        config = self._current_state_config(request)
        if request.method == "GET":
            return Response(StatePolicyConfigSerializer(config).data)

        old_value = getattr(config, field_name)
        serializer = StatePolicyConfigSerializer(
            config,
            data={field_name: request.data.get(field_name, request.data)},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        log_action(
            action=AuditAction.UPDATE,
            actor=request.user,
            target=config,
            old_value={field_name: old_value},
            new_value={field_name: getattr(config, field_name)},
            metadata={"event": event_name, "module": "Account Settings"},
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get", "patch"], url_path="my-state-profile")
    def my_state_profile(self, request):
        return self._settings_action(
            request,
            field_name="state_profile_settings",
            event_name="state_profile_settings_updated",
        )

    @action(detail=False, methods=["get", "patch"], url_path="my-notification-settings")
    def my_notification_settings(self, request):
        return self._settings_action(
            request,
            field_name="notification_settings",
            event_name="notification_settings_updated",
        )

    @action(detail=False, methods=["get", "patch"], url_path="my-security-access-settings")
    def my_security_access_settings(self, request):
        return self._settings_action(
            request,
            field_name="security_access_settings",
            event_name="security_access_settings_updated",
        )

    @action(detail=False, methods=["get"], url_path="my-audit-logs")
    def my_audit_logs(self, request):
        user = request.user
        if user.role != UserRole.STATE_ADMIN:
            raise PermissionDenied("Only state admins can view state audit logs.")
        if not user.state_id:
            raise PermissionDenied("State admin account is not linked to a state.")

        queryset = AuditLog.objects.select_related("actor", "state").filter(state=user.state).order_by("-created_at")
        action_filter = request.query_params.get("action")
        module_filter = request.query_params.get("module")
        search = request.query_params.get("search")
        if action_filter:
            queryset = queryset.filter(action=action_filter)
        if module_filter:
            queryset = queryset.filter(metadata__module=module_filter)
        if search:
            queryset = queryset.filter(metadata__icontains=search)
        return Response(StateAuditLogSerializer(queryset[:100], many=True).data)
