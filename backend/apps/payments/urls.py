from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.payments.views import (
    AssessmentFeeViewSet,
    InitiateAssessmentPaymentView,
    InitiateSubscriptionPaymentView,
    PaymentTransactionViewSet,
    PaymentWebhookView,
    VerifyPaymentView,
)


router = DefaultRouter()
router.register("assessment-fees", AssessmentFeeViewSet, basename="assessment-fees")
router.register("payments", PaymentTransactionViewSet, basename="payments")

urlpatterns = [
    path("payments/assessment/initiate/", InitiateAssessmentPaymentView.as_view(), name="initiate-assessment-payment"),
    path("payments/subscription/initiate/", InitiateSubscriptionPaymentView.as_view(), name="initiate-subscription-payment"),
    path("payments/verify/<str:reference>/", VerifyPaymentView.as_view(), name="verify-payment"),
    path("payments/webhook/", PaymentWebhookView.as_view(), name="payment-webhook"),
    *router.urls,
]
