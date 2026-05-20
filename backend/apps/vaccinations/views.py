from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.vaccinations.models import VaccinationRecord
from apps.vaccinations.serializers import VaccinationRecordSerializer


class VaccinationRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VaccinationRecord.objects.select_related(
        "food_handler",
        "assessment",
        "assessment__facility",
        "recorded_by",
    ).order_by("-created_at")
    serializer_class = VaccinationRecordSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["food_handler", "assessment", "vaccine_type", "status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        queryset = self.queryset
        food_handler_id = self.kwargs.get("food_handler_id")
        if food_handler_id:
            queryset = queryset.filter(food_handler_id=food_handler_id)
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return queryset
        if user.role in {UserRole.STATE_ADMIN, UserRole.INSPECTOR}:
            return queryset.filter(food_handler__state=user.state)
        if user.role == UserRole.FOOD_HANDLER:
            return queryset.filter(food_handler__user=user)
        if user.role == UserRole.EMPLOYER and hasattr(user, "employer"):
            return queryset.filter(food_handler__employer=user.employer)
        if user.organization_id:
            return queryset.filter(assessment__facility__organization=user.organization)
        return queryset.none()
