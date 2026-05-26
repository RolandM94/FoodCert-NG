from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsActiveUser
from apps.employers.models import Employer
from apps.payments.models import PaymentStatus
from apps.payments.permissions import ensure_employer_billing_access, is_platform_finance_user
from apps.payments.serializers import PaymentTransactionSerializer
from apps.payments.services import PaymentService
from apps.subscriptions.models import EmployerInvoice, EmployerSubscriptionPlan
from apps.subscriptions.serializers import (
    EmployerInvoiceSerializer,
    EmployerSubscribeSerializer,
    EmployerSubscriptionChangePlanSerializer,
    EmployerSubscriptionCheckoutSerializer,
    EmployerSubscriptionPlanSerializer,
    EmployerSubscriptionSerializer,
)
from apps.subscriptions.services import EmployerInvoiceService, EmployerSubscriptionService


class EmployerSubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = EmployerSubscriptionPlan.objects.order_by("price_monthly", "name")
    serializer_class = EmployerSubscriptionPlanSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["status"]
    ordering_fields = ["price_monthly", "price_yearly", "created_at"]

    def perform_create(self, serializer):
        if not is_platform_finance_user(self.request.user):
            raise PermissionDenied("Only federal admins can manage subscription plans.")
        serializer.save()

    def perform_update(self, serializer):
        if not is_platform_finance_user(self.request.user):
            raise PermissionDenied("Only federal admins can manage subscription plans.")
        serializer.save()


class EmployerSubscribeView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=EmployerSubscribeSerializer, responses={201: EmployerSubscriptionSerializer})
    def post(self, request, employer_id):
        employer = get_object_or_404(Employer, id=employer_id)
        ensure_employer_billing_access(request.user, employer, manage=True)
        serializer = EmployerSubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = _checkout_subscription(
            user=request.user,
            employer=employer,
            plan=serializer.validated_data["plan"],
            billing_cycle=serializer.validated_data["billing_cycle"],
        )
        return Response(EmployerSubscriptionSerializer(subscription).data, status=201)


class EmployerCurrentSubscriptionView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=EmployerSubscriptionSerializer)
    def get(self, request, employer_id):
        employer = get_object_or_404(Employer, id=employer_id)
        ensure_employer_billing_access(request.user, employer)
        subscription = EmployerSubscriptionService.current_for_employer(employer)
        if not subscription:
            return Response(None)
        return Response(EmployerSubscriptionSerializer(subscription).data)


class EmployerSubscriptionCheckoutView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=EmployerSubscriptionCheckoutSerializer, responses={201: EmployerSubscriptionSerializer})
    def post(self, request, employer_id):
        employer = get_object_or_404(Employer, id=employer_id)
        ensure_employer_billing_access(request.user, employer, manage=True)
        serializer = EmployerSubscriptionCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = _checkout_subscription(
            user=request.user,
            employer=employer,
            plan=serializer.validated_data["plan"],
            billing_cycle=serializer.validated_data["billing_cycle"],
        )
        return Response(EmployerSubscriptionSerializer(subscription).data, status=201)


class EmployerSubscriptionChangePlanView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=EmployerSubscriptionChangePlanSerializer, responses={200: EmployerSubscriptionSerializer})
    def patch(self, request, employer_id):
        employer = get_object_or_404(Employer, id=employer_id)
        ensure_employer_billing_access(request.user, employer, manage=True)
        serializer = EmployerSubscriptionChangePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction_obj = PaymentService.initiate_subscription_payment(
            payer_user=request.user,
            employer=employer,
            plan=serializer.validated_data["plan"],
            billing_cycle=serializer.validated_data["billing_cycle"],
        )
        invoice = EmployerInvoiceService.create_for_subscription_checkout(
            employer=employer,
            plan=serializer.validated_data["plan"],
            billing_cycle=serializer.validated_data["billing_cycle"],
            payment_transaction=transaction_obj,
            actor=request.user,
        )
        transaction_obj = PaymentService.verify_payment(reference=transaction_obj.internal_reference, actor=request.user)
        if transaction_obj.status != PaymentStatus.SUCCESS:
            raise ValidationError("Payment was not successful.")
        subscription = EmployerSubscriptionService.change_plan(
            employer=employer,
            plan=serializer.validated_data["plan"],
            billing_cycle=serializer.validated_data["billing_cycle"],
            payment_transaction=transaction_obj,
            actor=request.user,
        )
        EmployerInvoiceService.mark_paid(invoice=invoice, subscription=subscription, actor=request.user)
        return Response(EmployerSubscriptionSerializer(subscription).data)


class EmployerInvoiceListView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=EmployerInvoiceSerializer(many=True))
    def get(self, request, employer_id):
        employer = get_object_or_404(Employer, id=employer_id)
        ensure_employer_billing_access(request.user, employer)
        invoices = (
            EmployerInvoice.objects.filter(employer=employer)
            .select_related("subscription__plan", "payment_transaction")
            .order_by("-issued_at")
        )
        return Response(EmployerInvoiceSerializer(invoices, many=True).data)


class EmployerPaymentListView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=PaymentTransactionSerializer(many=True))
    def get(self, request, employer_id):
        employer = get_object_or_404(Employer, id=employer_id)
        ensure_employer_billing_access(request.user, employer)
        transactions = (
            employer.invoices.filter(payment_transaction__isnull=False)
            .select_related("payment_transaction__payer_user")
            .order_by("-issued_at")
        )
        payments = [invoice.payment_transaction for invoice in transactions]
        return Response(PaymentTransactionSerializer(payments, many=True).data)


def _checkout_subscription(*, user, employer, plan, billing_cycle):
    transaction_obj = PaymentService.initiate_subscription_payment(
        payer_user=user,
        employer=employer,
        plan=plan,
        billing_cycle=billing_cycle,
    )
    invoice = EmployerInvoiceService.create_for_subscription_checkout(
        employer=employer,
        plan=plan,
        billing_cycle=billing_cycle,
        payment_transaction=transaction_obj,
        actor=user,
    )
    transaction_obj = PaymentService.verify_payment(reference=transaction_obj.internal_reference, actor=user)
    if transaction_obj.status != PaymentStatus.SUCCESS:
        raise ValidationError("Payment was not successful.")
    subscription = EmployerSubscriptionService.activate(
        employer=employer,
        plan=plan,
        billing_cycle=billing_cycle,
        payment_transaction=transaction_obj,
        actor=user,
    )
    EmployerInvoiceService.mark_paid(invoice=invoice, subscription=subscription, actor=user)
    return subscription
