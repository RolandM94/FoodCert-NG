from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.subscriptions.views import (
    EmployerCurrentSubscriptionView,
    EmployerInvoiceListView,
    EmployerPaymentListView,
    EmployerSubscribeView,
    EmployerSubscriptionChangePlanView,
    EmployerSubscriptionCheckoutView,
    EmployerSubscriptionPlanViewSet,
)


router = DefaultRouter()
router.register("subscription-plans", EmployerSubscriptionPlanViewSet, basename="subscription-plans")

urlpatterns = [
    path("employers/<uuid:employer_id>/subscribe/", EmployerSubscribeView.as_view(), name="employer-subscribe"),
    path("employers/<uuid:employer_id>/subscription/", EmployerCurrentSubscriptionView.as_view(), name="employer-current-subscription"),
    path("employers/<uuid:employer_id>/subscription/checkout/", EmployerSubscriptionCheckoutView.as_view(), name="employer-subscription-checkout"),
    path("employers/<uuid:employer_id>/subscription/change-plan/", EmployerSubscriptionChangePlanView.as_view(), name="employer-subscription-change-plan"),
    path("employers/<uuid:employer_id>/invoices/", EmployerInvoiceListView.as_view(), name="employer-invoices"),
    path("employers/<uuid:employer_id>/payments/", EmployerPaymentListView.as_view(), name="employer-payments"),
    *router.urls,
]
