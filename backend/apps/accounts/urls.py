from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import (
    AcceptInviteView,
    AuthTokenRefreshView,
    AuthTokenView,
    LogoutView,
    OrganizationInviteViewSet,
    PasswordResetView,
    RegisterViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register("auth/register", RegisterViewSet, basename="auth-register")
router.register("users", UserViewSet, basename="users")

invite_list = OrganizationInviteViewSet.as_view({"get": "list", "post": "create"})
invite_detail = OrganizationInviteViewSet.as_view({"delete": "destroy", "get": "retrieve"})

urlpatterns = [
    path("auth/login/", AuthTokenView.as_view(), name="token-obtain-pair"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/token/refresh/", AuthTokenRefreshView.as_view(), name="token-refresh"),
    path("auth/password-reset/", PasswordResetView.as_view(), name="auth-password-reset"),
    path("organizations/<uuid:organization_id>/invites/", invite_list, name="organization-invites"),
    path("organizations/<uuid:organization_id>/invites/<uuid:pk>/", invite_detail, name="organization-invite-detail"),
    path("invites/<str:token>/accept/", AcceptInviteView.as_view(), name="accept-invite"),
    path("", include(router.urls)),
]
