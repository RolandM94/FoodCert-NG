from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import (
    AcceptInviteView,
    AuthTokenRefreshView,
    AuthTokenView,
    DeclineInviteView,
    InvitePreviewView,
    LogoutView,
    MyEffectivePermissionsView,
    MyMembershipsView,
    OrganizationInviteViewSet,
    PasswordResetView,
    PermissionCheckView,
    RegisterViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register("auth/register", RegisterViewSet, basename="auth-register")
router.register("users", UserViewSet, basename="users")

invite_list = OrganizationInviteViewSet.as_view({"get": "list", "post": "create"})
invite_detail = OrganizationInviteViewSet.as_view({"delete": "destroy", "get": "retrieve"})
invite_resend = OrganizationInviteViewSet.as_view({"post": "resend"})
invite_revoke = OrganizationInviteViewSet.as_view({"post": "revoke"})

urlpatterns = [
    path("auth/login/", AuthTokenView.as_view(), name="token-obtain-pair"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/token/refresh/", AuthTokenRefreshView.as_view(), name="token-refresh"),
    path("auth/password-reset/", PasswordResetView.as_view(), name="auth-password-reset"),
    path("me/memberships/", MyMembershipsView.as_view(), name="me-memberships"),
    path("me/effective-permissions/", MyEffectivePermissionsView.as_view(), name="me-effective-permissions"),
    path("permissions/check/", PermissionCheckView.as_view(), name="permission-check"),
    path("organizations/<uuid:organization_id>/invites/", invite_list, name="organization-invites"),
    path("organizations/<uuid:organization_id>/invites/<uuid:pk>/", invite_detail, name="organization-invite-detail"),
    path("organizations/<uuid:organization_id>/invites/<uuid:pk>/resend/", invite_resend, name="organization-invite-resend"),
    path("organizations/<uuid:organization_id>/invites/<uuid:pk>/revoke/", invite_revoke, name="organization-invite-revoke"),
    path("invites/<str:token>/preview/", InvitePreviewView.as_view(), name="preview-invite"),
    path("invites/<str:token>/accept/", AcceptInviteView.as_view(), name="accept-invite"),
    path("invites/<str:token>/decline/", DeclineInviteView.as_view(), name="decline-invite"),
    path("", include(router.urls)),
]
