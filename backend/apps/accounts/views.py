from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.models import UserInvite, UserRole
from apps.accounts.permissions import IsActiveUser, IsSelfOrScopedAdmin
from apps.accounts.serializers import (
    AcceptInviteSerializer,
    InviteUserSerializer,
    InvitePreviewSerializer,
    PasswordResetSerializer,
    FoodCertTokenObtainPairSerializer,
    RegisterSerializer,
    UserInviteSerializer,
    UserAdminSerializer,
    UserSerializer,
    UserStatusSerializer,
    UserUnitAssignmentSerializer,
)
from apps.accounts.services import InviteService
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.common.throttles import LoginRateThrottle
from apps.organizations.models import MembershipStatus, Organization
from apps.organizations.serializers_access import EffectivePermissionCheckSerializer
from apps.organizations.serializers_membership import MembershipListSerializer
from apps.organizations.services_access import EffectiveAccessService

User = get_user_model()


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.none()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        log_action(action=AuditAction.CREATE, target=user, metadata={"source": "public_register"})


class AuthTokenView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = FoodCertTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        identifier = request.data.get("username") or request.data.get("email") or ""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            user = User.objects.filter(username=identifier).first() or User.objects.filter(email=identifier).first()
            if user and user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.FACILITY_ADMIN}:
                log_action(
                    action=AuditAction.SECURITY_EVENT,
                    actor=user,
                    target=user,
                    request=request,
                    metadata={"event": "high_privilege_login_failure", "identifier": identifier},
                )
            raise exc
        log_action(action=AuditAction.LOGIN, actor=serializer.user, target=serializer.user, request=request, metadata={"event": "login_success"})
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AuthTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        refresh = request.data.get("refresh")
        if refresh:
            RefreshToken(refresh).blacklist()
        log_action(action=AuditAction.UPDATE, actor=request.user, target=request.user, metadata={"event": "logout"})
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetView(APIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "If the email exists, password reset instructions will be sent."})


class MyMembershipsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        memberships = (
            request.user.memberships.select_related("user", "organization", "role", "unit")
            .filter(status=MembershipStatus.ACTIVE)
            .order_by("organization__name", "role__name")
        )
        return Response(MembershipListSerializer(memberships, many=True).data)


class MyEffectivePermissionsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        organization_id = request.query_params.get("organization_id")
        organization = None
        if organization_id:
            organization = get_object_or_404(Organization, id=organization_id)
        permissions = EffectiveAccessService().list_permissions(request.user, organization=organization)
        return Response({"permissions": permissions})


class PermissionCheckView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def post(self, request):
        serializer = EffectivePermissionCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = EffectiveAccessService().check(
            request.user,
            serializer.validated_data["permission_code"],
            organization=serializer.validated_data.get("organization"),
        )
        return Response(result.as_dict())


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("organization", "unit", "state").order_by("-created_at")
    permission_classes = [IsAuthenticated, IsActiveUser, IsSelfOrScopedAdmin]
    http_method_names = ["get", "patch", "post", "head", "options"]

    def get_serializer_class(self):
        if self.action == "invite":
            return InviteUserSerializer
        if self.action == "status":
            return UserStatusSerializer
        if self.action == "unit":
            return UserUnitAssignmentSerializer
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return UserSerializer
        if self.request.user.role == UserRole.SUPER_ADMIN:
            return UserAdminSerializer
        return UserSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return super().get_queryset()
        user = self.request.user
        queryset = super().get_queryset()
        if user.role == UserRole.SUPER_ADMIN:
            return queryset
        if user.role == UserRole.FEDERAL_ADMIN:
            return queryset
        if user.role == UserRole.STATE_ADMIN:
            return queryset.filter(state=user.state)
        if user.organization_id:
            return queryset.filter(organization=user.organization)
        return queryset.filter(pk=user.pk)

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use /api/users/invite/ to add organization users."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        if request.method == "GET":
            return Response(UserSerializer(request.user).data)

        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_action(action=AuditAction.UPDATE, actor=request.user, target=request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="invite")
    def invite(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_action(action=AuditAction.CREATE, actor=request.user, target=user, metadata={"event": "invite"})
        return Response(UserAdminSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="status")
    def status(self, request, pk=None):
        target_user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.STATE_ADMIN, UserRole.FACILITY_ADMIN}:
            return Response({"detail": "You cannot change user status."}, status=status.HTTP_403_FORBIDDEN)
        if target_user.pk == request.user.pk:
            return Response({"detail": "You cannot change your own status."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.status = serializer.validated_data["status"]
        target_user.save(update_fields=["status", "updated_at"])
        log_action(
            action=AuditAction.ROLE_CHANGE,
            actor=request.user,
            target=target_user,
            metadata={"status": target_user.status},
        )
        return Response(UserAdminSerializer(target_user).data)

    @action(detail=True, methods=["patch"], url_path="unit")
    def unit(self, request, pk=None):
        target_user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unit = serializer.validated_data.get("unit")
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.FACILITY_ADMIN, UserRole.EMPLOYER}:
            return Response({"detail": "You cannot assign user units."}, status=status.HTTP_403_FORBIDDEN)
        if unit and unit.organization_id != target_user.organization_id:
            return Response({"detail": "Unit must belong to the user's organization."}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.role in {UserRole.FACILITY_ADMIN, UserRole.EMPLOYER} and target_user.organization_id != request.user.organization_id:
            return Response({"detail": "You can only assign users in your organization."}, status=status.HTTP_403_FORBIDDEN)
        if request.user.role == UserRole.STATE_ADMIN and target_user.state_id != request.user.state_id:
            return Response({"detail": "State admins can only assign users in their state."}, status=status.HTTP_403_FORBIDDEN)
        target_user.unit = unit
        if "unit_restricted" in serializer.validated_data:
            target_user.unit_restricted = serializer.validated_data["unit_restricted"]
        elif unit is None:
            target_user.unit_restricted = False
        target_user.save(update_fields=["unit", "unit_restricted", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=request.user, target=target_user, metadata={"event": "unit_assigned"})
        return Response(UserAdminSerializer(target_user).data)


class OrganizationInviteViewSet(viewsets.ModelViewSet):
    serializer_class = UserInviteSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_organization(self):
        return Organization.objects.get(id=self.kwargs["organization_id"])

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return UserInvite.objects.select_related("organization", "unit", "invited_by", "accepted_by")
        organization_id = self.kwargs["organization_id"]
        queryset = UserInvite.objects.select_related("organization", "unit", "invited_by", "accepted_by").filter(organization_id=organization_id)
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
        InviteService.validate_invite_scope(
            actor=self.request.user,
            organization=organization,
            role=serializer.validated_data["role"],
            unit=serializer.validated_data.get("unit"),
        )
        invite = InviteService.create_invite(
            actor=self.request.user,
            organization=organization,
            email=serializer.validated_data["email"],
            role=serializer.validated_data["role"],
            unit=serializer.validated_data.get("unit"),
            unit_restricted=serializer.validated_data.get("unit_restricted", False),
            phone=serializer.validated_data.get("phone", ""),
            message=serializer.validated_data.get("message", ""),
            expires_at=serializer.validated_data.get("expires_at"),
            ministry_staff_role=serializer.validated_data.get("ministry_staff_role", ""),
        )
        serializer.instance = invite

    def destroy(self, request, *args, **kwargs):
        invite = self.get_object()
        invite = InviteService.revoke(invite=invite, actor=request.user)
        return Response(UserInviteSerializer(invite).data)

    @action(detail=True, methods=["post"], url_path="resend")
    def resend(self, request, organization_id=None, pk=None):
        invite = InviteService.resend(invite=self.get_object(), actor=request.user)
        return Response(UserInviteSerializer(invite).data)

    @action(detail=True, methods=["post"], url_path="revoke")
    def revoke(self, request, organization_id=None, pk=None):
        invite = InviteService.revoke(invite=self.get_object(), actor=request.user)
        return Response(UserInviteSerializer(invite).data)


class AcceptInviteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=AcceptInviteSerializer, responses=UserSerializer)
    def post(self, request, token):
        invite = get_object_or_404(UserInvite.objects.select_related("organization", "unit", "invited_by"), token=token)
        serializer = AcceptInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, invite = InviteService.accept(invite=invite, payload=serializer.validated_data, actor=request.user)
        return Response({"user": UserSerializer(user).data, "invite": UserInviteSerializer(invite).data})


class DeclineInviteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=None, responses=UserInviteSerializer)
    def post(self, request, token):
        invite = get_object_or_404(UserInvite.objects.select_related("organization", "unit", "invited_by"), token=token)
        invite = InviteService.decline(invite=invite, actor=request.user)
        return Response(UserInviteSerializer(invite).data)


class InvitePreviewView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        invite = get_object_or_404(UserInvite.objects.select_related("organization", "unit", "invited_by"), token=token)
        return Response(InvitePreviewSerializer(invite).data)
