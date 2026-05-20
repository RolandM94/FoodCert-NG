from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.employers.models import Employer
from apps.payments.models import PaymentStatus
from apps.payments.services import PaymentService
from apps.subscriptions.models import EmployerSubscriptionPlan
from apps.subscriptions.serializers import (
    EmployerSubscribeSerializer,
    EmployerSubscriptionPlanSerializer,
    EmployerSubscriptionSerializer,
)
from apps.subscriptions.services import EmployerSubscriptionService


class EmployerSubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = EmployerSubscriptionPlan.objects.order_by("price_monthly", "name")
    serializer_class = EmployerSubscriptionPlanSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["status"]
    ordering_fields = ["price_monthly", "price_yearly", "created_at"]

    def perform_create(self, serializer):
        if self.request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only federal admins can manage subscription plans.")
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only federal admins can manage subscription plans.")
        serializer.save()


class EmployerSubscribeView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=EmployerSubscribeSerializer, responses={201: EmployerSubscriptionSerializer})
    def post(self, request, employer_id):
        employer = get_object_or_404(Employer, id=employer_id)
        if request.user.role == UserRole.EMPLOYER and employer.user_id != request.user.id:
            raise PermissionDenied("You can only subscribe your own employer profile.")
        serializer = EmployerSubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction_obj = PaymentService.initiate_subscription_payment(
            payer_user=request.user,
            employer=employer,
            plan=serializer.validated_data["plan"],
            billing_cycle=serializer.validated_data["billing_cycle"],
        )
        transaction_obj = PaymentService.verify_payment(reference=transaction_obj.internal_reference, actor=request.user)
        if transaction_obj.status != PaymentStatus.SUCCESS:
            raise ValidationError("Payment was not successful.")
        subscription = EmployerSubscriptionService.activate(
            employer=employer,
            plan=serializer.validated_data["plan"],
            billing_cycle=serializer.validated_data["billing_cycle"],
            payment_transaction=transaction_obj,
            actor=request.user,
        )
        return Response(EmployerSubscriptionSerializer(subscription).data, status=201)


class EmployerCurrentSubscriptionView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=EmployerSubscriptionSerializer)
    def get(self, request, employer_id):
        employer = get_object_or_404(Employer, id=employer_id)
        if request.user.role == UserRole.EMPLOYER and employer.user_id != request.user.id:
            raise PermissionDenied("You can only view your own employer subscription.")
        subscription = EmployerSubscriptionService.current_for_employer(employer)
        if not subscription:
            return Response(None)
        return Response(EmployerSubscriptionSerializer(subscription).data)
