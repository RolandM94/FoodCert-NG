from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.nin_verification.models import NINVerification
from apps.nin_verification.serializers import NINOverrideSerializer, NINVerificationSerializer
from apps.nin_verification.services import NINVerificationService


class NINVerificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NINVerification.objects.select_related("food_handler", "food_handler__state", "reviewed_by").order_by("-created_at")
    serializer_class = NINVerificationSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        queryset = self.queryset
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return queryset.filter(food_handler__state=user.state)
        if user.role == UserRole.FOOD_HANDLER:
            return queryset.filter(food_handler__user=user)
        return queryset.none()

    def _ensure_regulator(self, verification):
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return
        if user.role == UserRole.STATE_ADMIN and verification.food_handler.state_id == user.state_id:
            return
        raise PermissionDenied("You cannot review this NIN verification.")

    @action(detail=True, methods=["patch"], url_path="approve-override")
    def approve_override(self, request, pk=None):
        verification = self.get_object()
        self._ensure_regulator(verification)
        serializer = NINOverrideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verification = NINVerificationService.approve_override(
            verification=verification,
            reviewer=request.user,
            notes=serializer.validated_data.get("review_notes", ""),
        )
        return Response(NINVerificationSerializer(verification).data)

    @action(detail=True, methods=["patch"], url_path="reject-override")
    def reject_override(self, request, pk=None):
        verification = self.get_object()
        self._ensure_regulator(verification)
        serializer = NINOverrideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verification = NINVerificationService.reject_override(
            verification=verification,
            reviewer=request.user,
            notes=serializer.validated_data.get("review_notes", ""),
        )
        return Response(NINVerificationSerializer(verification).data)
