import hashlib
import hmac

from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.employers.models import Employer
from apps.payments.models import AssessmentFee, PaymentTransaction
from apps.payments.serializers import (
    AssessmentFeeSerializer,
    InitiateAssessmentPaymentSerializer,
    InitiateSubscriptionPaymentSerializer,
    PaymentTransactionSerializer,
    PaymentWebhookSerializer,
)
from apps.payments.services import PaymentService
from apps.subscriptions.models import EmployerSubscriptionPlan


class AssessmentFeeViewSet(viewsets.ModelViewSet):
    queryset = AssessmentFee.objects.select_related("state", "created_by").order_by("-effective_from")
    serializer_class = AssessmentFeeSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["state", "facility_type", "status"]
    ordering_fields = ["created_at", "effective_from", "amount"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        if user.role == UserRole.STATE_ADMIN:
            return self.queryset.filter(state=user.state)
        return self.queryset.filter(status="active")

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("Only federal and state admins can configure assessment fees.")
        if user.role == UserRole.STATE_ADMIN and serializer.validated_data["state"] != user.state:
            raise PermissionDenied("State admins can only configure fees for their state.")
        self._validate_fee_split(serializer.validated_data)
        fee = serializer.save(created_by=user)
        log_action(action=AuditAction.CREATE, actor=user, target=fee)

    def perform_update(self, serializer):
        user = self.request.user
        if user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("Only federal and state admins can update assessment fees.")
        instance = self.get_object()
        target_state = serializer.validated_data.get("state", instance.state)
        if user.role == UserRole.STATE_ADMIN and target_state != user.state:
            raise PermissionDenied("State admins can only update fees for their state.")
        validated = {
            "amount": serializer.validated_data.get("amount", instance.amount),
            "state_fee": serializer.validated_data.get("state_fee", instance.state_fee),
            "facility_fee": serializer.validated_data.get("facility_fee", instance.facility_fee),
            "platform_fee": serializer.validated_data.get("platform_fee", instance.platform_fee),
        }
        self._validate_fee_split(validated)
        fee = serializer.save()
        log_action(action=AuditAction.UPDATE, actor=user, target=fee)

    def _validate_fee_split(self, data):
        total = data["state_fee"] + data["facility_fee"] + data["platform_fee"]
        if total != data["amount"]:
            raise ValidationError("State, facility, and platform fees must equal the gross amount.")


class PaymentTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentTransaction.objects.select_related("payer_user").order_by("-created_at")
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["status", "payer_type", "related_entity_type"]
    ordering_fields = ["created_at", "amount", "paid_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        if user.role == UserRole.STATE_ADMIN:
            return self.queryset.filter(metadata__state_id=str(user.state_id))
        return self.queryset.filter(payer_user=user)


class InitiateAssessmentPaymentView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=InitiateAssessmentPaymentSerializer, responses={201: PaymentTransactionSerializer})
    def post(self, request):
        serializer = InitiateAssessmentPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            transaction_obj = PaymentService.initiate_assessment_payment(
                payer_user=request.user,
                facility=serializer.validated_data["facility"],
                food_handler_id=serializer.validated_data["food_handler_id"],
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(PaymentTransactionSerializer(transaction_obj).data, status=201)


class InitiateSubscriptionPaymentView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=InitiateSubscriptionPaymentSerializer, responses={201: PaymentTransactionSerializer})
    def post(self, request):
        serializer = InitiateSubscriptionPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employer = get_object_or_404(Employer, id=serializer.validated_data["employer_id"])
        plan = get_object_or_404(EmployerSubscriptionPlan, id=serializer.validated_data["plan_id"])
        if request.user.role == UserRole.EMPLOYER and employer.user_id != request.user.id:
            raise PermissionDenied("You can only subscribe your own employer profile.")
        transaction_obj = PaymentService.initiate_subscription_payment(
            payer_user=request.user,
            employer=employer,
            plan=plan,
            billing_cycle=serializer.validated_data["billing_cycle"],
        )
        return Response(PaymentTransactionSerializer(transaction_obj).data, status=201)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=PaymentTransactionSerializer)
    def get(self, request, reference):
        try:
            transaction_obj = PaymentService.verify_payment(reference=reference, actor=request.user)
        except PaymentTransaction.DoesNotExist:
            raise NotFound("Payment transaction was not found.")
        return Response(PaymentTransactionSerializer(transaction_obj).data)


class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=PaymentWebhookSerializer, responses=PaymentTransactionSerializer)
    def post(self, request):
        if settings.PAYMENT_WEBHOOK_SECRET:
            signature = request.headers.get("X-FoodCert-Signature", "")
            expected = hmac.new(
                settings.PAYMENT_WEBHOOK_SECRET.encode("utf-8"),
                request.body,
                hashlib.sha256,
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                raise PermissionDenied("Invalid payment webhook signature.")
        serializer = PaymentWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction_obj = PaymentService.verify_payment(reference=serializer.validated_data["reference"])
        log_action(action=AuditAction.PAYMENT_EVENT, target=transaction_obj, metadata={"event": "payment_webhook"})
        return Response(PaymentTransactionSerializer(transaction_obj).data)
