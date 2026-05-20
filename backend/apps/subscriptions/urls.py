from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.subscriptions.views import (
    EmployerSubscribeView,
    EmployerSubscriptionPlanViewSet,
)


router = DefaultRouter()
router.register("subscription-plans", EmployerSubscriptionPlanViewSet, basename="subscription-plans")

urlpatterns = [
    path("employers/<uuid:employer_id>/subscribe/", EmployerSubscribeView.as_view(), name="employer-subscribe"),
    *router.urls,
]
