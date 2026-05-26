from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.payments.views import (
    AssessmentFeeViewSet,
    AssessmentPaymentInitializeView,
    AssessmentPaymentQuoteView,
    EmployerBulkAssessmentPaymentInitializeView,
    EmployerBulkAssessmentPaymentQuoteView,
    InitiateAssessmentPaymentView,
    InitiateSubscriptionPaymentView,
    PaymentProviderViewSet,
    PaymentChargebackView,
    PaymentReconciliationRecordViewSet,
    PaymentTransactionViewSet,
    PaymentReceiptView,
    PaymentRefundRequestListView,
    PaymentRefundRequestView,
    RefundRequestViewSet,
    PaymentWebhookEventViewSet,
    PaymentWebhookView,
    VerifyPaymentView,
)


router = DefaultRouter()
router.register("assessment-fees", AssessmentFeeViewSet, basename="assessment-fees")
router.register("admin/payment-providers", PaymentProviderViewSet, basename="payment-providers")
router.register("admin/payment-reconciliations", PaymentReconciliationRecordViewSet, basename="admin-payment-reconciliations")
router.register("state/finance/reconciliation", PaymentReconciliationRecordViewSet, basename="state-payment-reconciliation")
router.register("federal/finance/reconciliation", PaymentReconciliationRecordViewSet, basename="federal-payment-reconciliation")
router.register("admin/payment-webhook-events", PaymentWebhookEventViewSet, basename="payment-webhook-events")
router.register("admin/refunds", RefundRequestViewSet, basename="admin-refunds")
router.register("payments", PaymentTransactionViewSet, basename="payments")

urlpatterns = [
    path("payments/assessment/<uuid:assessment_id>/fee/", AssessmentPaymentQuoteView.as_view(), name="assessment-payment-fee"),
    path("payments/assessment/<uuid:assessment_id>/initialize/", AssessmentPaymentInitializeView.as_view(), name="assessment-payment-initialize"),
    path("payments/assessment/initiate/", InitiateAssessmentPaymentView.as_view(), name="initiate-assessment-payment"),
    path("payments/employers/<uuid:employer_id>/bulk-assessments/quote/", EmployerBulkAssessmentPaymentQuoteView.as_view(), name="employer-bulk-assessment-payment-quote"),
    path("payments/employers/<uuid:employer_id>/bulk-assessments/initialize/", EmployerBulkAssessmentPaymentInitializeView.as_view(), name="employer-bulk-assessment-payment-initialize"),
    path("payments/subscription/initiate/", InitiateSubscriptionPaymentView.as_view(), name="initiate-subscription-payment"),
    path("payments/verify/<str:reference>/", VerifyPaymentView.as_view(), name="verify-payment"),
    path("payments/transactions/<uuid:transaction_id>/receipt/", PaymentReceiptView.as_view(), name="payment-receipt"),
    path("payments/transactions/<uuid:transaction_id>/refund-requests/", PaymentRefundRequestListView.as_view(), name="payment-refund-requests"),
    path("payments/transactions/<uuid:transaction_id>/refund-request/", PaymentRefundRequestView.as_view(), name="payment-refund-request"),
    path("payments/webhook/", PaymentWebhookView.as_view(), name="payment-webhook"),
    path("payments/webhooks/<str:provider_code>/", PaymentWebhookView.as_view(), name="provider-payment-webhook"),
    path("payments/chargeback/", PaymentChargebackView.as_view(), name="payment-chargeback"),
    *router.urls,
]
