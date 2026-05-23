from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.facilities.models import MedicalFacility
from apps.payments.models import PaymentTransaction
from apps.settlements.models import Settlement
from apps.settlements.serializers import CreateSettlementSerializer, SettlementDisputeSerializer, SettlementSerializer
from apps.settlements.services import SettlementService


class SettlementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Settlement.objects.select_related("facility", "state", "payment_transaction").order_by("-created_at")
    serializer_class = SettlementSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["settlement_status", "state", "facility"]
    ordering_fields = ["created_at", "gross_amount", "settled_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if user.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return self.queryset
        if user.role == UserRole.STATE_ADMIN:
            return self.queryset.filter(state=user.state)
        if user.organization_id:
            return self.queryset.filter(facility__organization=user.organization)
        return self.queryset.none()

    @action(detail=False, methods=["post"], url_path="create-from-payment")
    def create_from_payment(self, request):
        serializer = CreateSettlementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction_obj = get_object_or_404(PaymentTransaction, id=serializer.validated_data["payment_transaction"])
        try:
            settlement = SettlementService.create_for_assessment_payment(
                payment_transaction=transaction_obj,
                assessment_id=serializer.validated_data.get("assessment"),
                actor=request.user,
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(SettlementSerializer(settlement).data, status=201)

    @action(detail=True, methods=["post"], url_path="process")
    def process(self, request, pk=None):
        settlement = self.get_object()
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("You cannot process settlements.")
        settlement = SettlementService.process(settlement=settlement, actor=request.user)
        return Response(SettlementSerializer(settlement).data)

    @extend_schema(request=SettlementDisputeSerializer, responses=SettlementSerializer)
    @action(detail=True, methods=["post"], url_path="dispute")
    def dispute(self, request, pk=None):
        serializer = SettlementDisputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        settlement = SettlementService.dispute(
            settlement=self.get_object(),
            actor=request.user,
            reason=serializer.validated_data["reason"],
        )
        return Response(SettlementSerializer(settlement).data)

    @action(detail=False, methods=["get"], url_path="facilities/(?P<facility_id>[^/.]+)")
    def by_facility(self, request, facility_id=None):
        facility = get_object_or_404(MedicalFacility, id=facility_id)
        queryset = self.get_queryset().filter(facility=facility)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(SettlementSerializer(page, many=True).data)
        return Response(SettlementSerializer(queryset, many=True).data)


class FacilitySettlementsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=SettlementSerializer(many=True))
    def get(self, request, facility_id):
        facility = get_object_or_404(MedicalFacility, id=facility_id)
        SettlementService.ensure_facility_finance_access(user=request.user, facility=facility)
        queryset = Settlement.objects.select_related("facility", "state", "payment_transaction", "disputed_by").filter(facility=facility)
        if request.query_params.get("status"):
            queryset = queryset.filter(settlement_status=request.query_params["status"])
        if request.query_params.get("dispute_status"):
            queryset = queryset.filter(dispute_status=request.query_params["dispute_status"])
        if request.query_params.get("date_from"):
            queryset = queryset.filter(created_at__date__gte=request.query_params["date_from"])
        if request.query_params.get("date_to"):
            queryset = queryset.filter(created_at__date__lte=request.query_params["date_to"])
        return Response(SettlementSerializer(queryset, many=True).data)


class FacilitySettlementDetailView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=SettlementSerializer)
    def get(self, request, facility_id, settlement_id):
        facility = get_object_or_404(MedicalFacility, id=facility_id)
        SettlementService.ensure_facility_finance_access(user=request.user, facility=facility)
        settlement = get_object_or_404(
            Settlement.objects.select_related("facility", "state", "payment_transaction", "disputed_by"),
            id=settlement_id,
            facility=facility,
        )
        log_action(
            action=AuditAction.PAYMENT_EVENT,
            actor=request.user,
            target=settlement,
            request=request,
            metadata={"event": "facility_settlement_detail_read"},
        )
        return Response(SettlementSerializer(settlement).data)


class FacilitySettlementDisputeView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=SettlementDisputeSerializer, responses=SettlementSerializer)
    def post(self, request, facility_id, settlement_id):
        facility = get_object_or_404(MedicalFacility, id=facility_id)
        SettlementService.ensure_facility_finance_access(user=request.user, facility=facility)
        settlement = get_object_or_404(Settlement, id=settlement_id, facility=facility)
        serializer = SettlementDisputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        settlement = SettlementService.dispute(
            settlement=settlement,
            actor=request.user,
            reason=serializer.validated_data["reason"],
        )
        return Response(SettlementSerializer(settlement).data)


class FacilitySettlementReportView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request, facility_id):
        facility = get_object_or_404(MedicalFacility, id=facility_id)
        SettlementService.ensure_facility_finance_access(user=request.user, facility=facility)
        payload = SettlementService.facility_metrics(
            facility=facility,
            date_from=request.query_params.get("date_from"),
            date_to=request.query_params.get("date_to"),
        )
        log_action(
            action=AuditAction.PAYMENT_EVENT,
            actor=request.user,
            target=facility,
            request=request,
            metadata={"event": "facility_settlement_report_read"},
        )
        return Response(payload)
