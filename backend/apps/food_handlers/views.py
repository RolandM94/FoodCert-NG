from uuid import uuid4

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.food_handlers.models import FoodHandlerProfile
from apps.food_handlers.serializers import (
    EmployerFoodHandlerListSerializer,
    FoodHandlerBranchAssignmentSerializer,
    FoodHandlerProfileSerializer,
)
from apps.nin_verification.serializers import NINVerificationSerializer
from apps.nin_verification.services import NINVerificationService


class FoodHandlerProfileViewSet(viewsets.ModelViewSet):
    queryset = FoodHandlerProfile.objects.select_related("user", "state", "lga", "employer", "business_branch").order_by("-created_at")
    serializer_class = FoodHandlerProfileSerializer
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
        if user.role == UserRole.EMPLOYER:
            if hasattr(user, "employer"):
                queryset = queryset.filter(employer=user.employer)
                if user.unit_restricted and user.unit_id:
                    queryset = queryset.filter(business_branch=user.unit)
            elif user.organization_id:
                queryset = queryset.filter(employer__organization=user.organization)
                if user.unit_restricted and user.unit_id:
                    queryset = queryset.filter(business_branch=user.unit)
            else:
                return queryset.none()
            return queryset
        if user.role == UserRole.FOOD_HANDLER:
            return queryset.filter(user=user)
        if user.organization_id:
            return queryset.filter(employer__organization=user.organization)
        return queryset.none()

    def get_serializer_class(self):
        if self.action == "business_branch":
            return FoodHandlerBranchAssignmentSerializer
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return FoodHandlerProfileSerializer
        if self.request.user.role == UserRole.EMPLOYER:
            return EmployerFoodHandlerListSerializer
        return FoodHandlerProfileSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != UserRole.FOOD_HANDLER:
            raise PermissionDenied("Only food handlers can create their own profile.")
        if FoodHandlerProfile.objects.filter(user=user).exists():
            raise PermissionDenied("Food handler profile already exists.")
        save_kwargs = {"user": user, "system_identifier": f"FCN-{uuid4().hex[:10].upper()}"}
        if user.unit_id and not serializer.validated_data.get("business_branch"):
            save_kwargs["business_branch"] = user.unit
        profile = serializer.save(**save_kwargs)
        log_action(action=AuditAction.CREATE, actor=user, target=profile)

    def perform_update(self, serializer):
        profile = self.get_object()
        user = self.request.user
        if user.role == UserRole.EMPLOYER:
            raise PermissionDenied("Employers cannot edit food handler medical identity records.")
        if user.role == UserRole.FOOD_HANDLER and profile.user_id != user.id:
            raise PermissionDenied("You can only update your own profile.")
        updated = serializer.save()
        log_action(action=AuditAction.UPDATE, actor=user, target=updated)

    @action(detail=True, methods=["patch"], url_path="business-branch")
    def business_branch(self, request, pk=None):
        profile = self.get_object()
        user = request.user
        if user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.EMPLOYER}:
            raise PermissionDenied("You cannot assign food handlers to branches.")
        if user.role == UserRole.STATE_ADMIN and profile.state_id != user.state_id:
            raise PermissionDenied("State admins can only update food handlers in their state.")
        if user.role == UserRole.EMPLOYER:
            if not profile.employer or profile.employer.organization_id != user.organization_id:
                raise PermissionDenied("Employers can only update their own food handlers.")
            if user.unit_restricted and user.unit_id and profile.business_branch_id not in {None, user.unit_id}:
                raise PermissionDenied("Branch managers can only manage food handlers in their branch.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        branch = serializer.validated_data.get("business_branch")
        if branch and profile.employer and branch.organization_id != profile.employer.organization_id:
            return Response({"detail": "Business branch must belong to the employer organization."}, status=status.HTTP_400_BAD_REQUEST)
        if user.role == UserRole.EMPLOYER and user.unit_restricted and user.unit_id and branch and branch.id != user.unit_id:
            raise PermissionDenied("Branch managers can only assign their own branch.")

        profile.business_branch = branch
        profile.save(update_fields=["business_branch", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=user, target=profile, metadata={"event": "business_branch_assigned"})
        return Response(FoodHandlerProfileSerializer(profile).data)

    @action(detail=True, methods=["post"], url_path="verify-nin")
    def verify_nin(self, request, pk=None):
        profile = self.get_object()
        user = request.user
        if user.role == UserRole.EMPLOYER:
            raise PermissionDenied("Employers cannot verify or view full NIN details.")
        if user.role == UserRole.FOOD_HANDLER and profile.user_id != user.id:
            raise PermissionDenied("You can only verify your own NIN.")
        verification = NINVerificationService.verify(food_handler=profile, actor=user)
        return Response(NINVerificationSerializer(verification).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="nin-verification")
    def nin_verification(self, request, pk=None):
        profile = self.get_object()
        if request.user.role == UserRole.EMPLOYER:
            raise PermissionDenied("Employers cannot view NIN verification details.")
        verification = profile.nin_verifications.order_by("-created_at").first()
        if not verification:
            return Response({"detail": "No NIN verification has been submitted."}, status=status.HTTP_404_NOT_FOUND)
        return Response(NINVerificationSerializer(verification).data)
