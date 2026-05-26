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
from apps.settlements.serializers import (
    CreateSettlementSerializer,
    EligibleSettlementAllocationSerializer,
    SettlementActionReasonSerializer,
    SettlementBatchCreateSerializer,
    SettlementBatchProcessSerializer,
    SettlementBatchSerializer,
    SettlementDisputeSerializer,
    SettlementDisputeResolutionSerializer,
    SettlementSerializer,
)
from apps.settlements.models import SettlementBatch
from apps.settlements.services import SettlementBatchService, SettlementService


class SettlementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Settlement.objects.select_related(
        "facility",
        "state",
        "payment_transaction",
        "payment_allocation",
        "fee_schedule",
    ).order_by("-created_at")
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
            result = SettlementService.create_for_assessment_payment(
                payment_transaction=transaction_obj,
                assessment_id=serializer.validated_data.get("assessment"),
                actor=request.user,
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        if isinstance(result, list):
            return Response(SettlementSerializer(result, many=True).data, status=201)
        return Response(SettlementSerializer(result).data, status=201)

    @action(detail=False, methods=["get"], url_path="eligible-allocations")
    def eligible_allocations(self, request):
        queryset = self.get_queryset()
        facility = None
        if request.query_params.get("facility"):
            facility = get_object_or_404(MedicalFacility, id=request.query_params["facility"])
            if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
                SettlementService.ensure_facility_finance_access(user=request.user, facility=facility)
        allocations = SettlementService.eligible_allocations(facility=facility)
        if request.user.role == UserRole.STATE_ADMIN:
            allocations = [allocation for allocation in allocations if allocation.state_id == request.user.state_id]
        elif request.user.organization_id and request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            allocations = [allocation for allocation in allocations if allocation.facility.organization_id == request.user.organization_id]
        return Response(EligibleSettlementAllocationSerializer(allocations, many=True).data)

    @action(detail=True, methods=["post"], url_path="process")
    def process(self, request, pk=None):
        settlement = self.get_object()
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("You cannot process settlements.")
        settlement = SettlementService.process(settlement=settlement, actor=request.user)
        return Response(SettlementSerializer(settlement).data)

    @extend_schema(request=SettlementActionReasonSerializer, responses=SettlementSerializer)
    @action(detail=True, methods=["post"], url_path="hold")
    def hold(self, request, pk=None):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("You cannot hold settlements.")
        serializer = SettlementActionReasonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        settlement = SettlementService.hold(
            settlement=self.get_object(),
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(SettlementSerializer(settlement).data)

    @action(detail=True, methods=["post"], url_path="release")
    def release(self, request, pk=None):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("You cannot release settlement holds.")
        settlement = SettlementService.release_hold(settlement=self.get_object(), actor=request.user)
        return Response(SettlementSerializer(settlement).data)

    @action(detail=True, methods=["post"], url_path="retry")
    def retry(self, request, pk=None):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("You cannot retry settlements.")
        settlement = SettlementService.retry_failed(settlement=self.get_object(), actor=request.user)
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

    @extend_schema(request=SettlementDisputeResolutionSerializer, responses=SettlementSerializer)
    @action(detail=True, methods=["post"], url_path="resolve-dispute")
    def resolve_dispute(self, request, pk=None):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}:
            raise PermissionDenied("You cannot resolve settlement disputes.")
        serializer = SettlementDisputeResolutionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        settlement = SettlementService.resolve_dispute(
            settlement=self.get_object(),
            actor=request.user,
            resolution=serializer.validated_data["resolution"],
            approved=serializer.validated_data["approved"],
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


class SettlementBatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SettlementBatch.objects.select_related("created_by", "approved_by", "processed_by").order_by("-created_at")
    serializer_class = SettlementBatchSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["status"]
    ordering_fields = ["created_at", "gross_amount", "processed_at"]

    def _ensure_platform_finance(self, request):
        if request.user.role not in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            raise PermissionDenied("Only platform finance users can manage settlement batches.")

    @extend_schema(request=SettlementBatchCreateSerializer, responses={201: SettlementBatchSerializer})
    @action(detail=False, methods=["post"], url_path="create")
    def create_batch(self, request):
        self._ensure_platform_finance(request)
        serializer = SettlementBatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        batch = SettlementBatchService.create(
            settlement_ids=serializer.validated_data["settlements"],
            actor=request.user,
        )
        return Response(SettlementBatchSerializer(batch).data, status=201)

    @action(detail=True, methods=["get"], url_path="settlements")
    def settlements(self, request, pk=None):
        self._ensure_platform_finance(request)
        batch = self.get_object()
        return Response(SettlementSerializer(batch.settlements.select_related("facility", "state", "payment_transaction", "payment_allocation", "fee_schedule"), many=True).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        self._ensure_platform_finance(request)
        batch = SettlementBatchService.approve(batch=self.get_object(), actor=request.user)
        return Response(SettlementBatchSerializer(batch).data)

    @extend_schema(request=SettlementBatchProcessSerializer, responses=SettlementBatchSerializer)
    @action(detail=True, methods=["post"], url_path="process")
    def process(self, request, pk=None):
        self._ensure_platform_finance(request)
        serializer = SettlementBatchProcessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        batch = SettlementBatchService.process(
            batch=self.get_object(),
            actor=request.user,
            fail=serializer.validated_data["simulate_failure"],
            failure_reason=serializer.validated_data.get("failure_reason", ""),
        )
        return Response(SettlementBatchSerializer(batch).data)

    @action(detail=True, methods=["post"], url_path="retry")
    def retry(self, request, pk=None):
        self._ensure_platform_finance(request)
        batch = SettlementBatchService.retry(batch=self.get_object(), actor=request.user)
        return Response(SettlementBatchSerializer(batch).data)


class FacilitySettlementsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=SettlementSerializer(many=True))
    def get(self, request, facility_id):
        facility = get_object_or_404(MedicalFacility, id=facility_id)
        SettlementService.ensure_facility_finance_access(user=request.user, facility=facility)
        queryset = Settlement.objects.select_related("facility", "state", "payment_transaction", "payment_allocation", "fee_schedule", "disputed_by").filter(facility=facility)
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
            Settlement.objects.select_related("facility", "state", "payment_transaction", "payment_allocation", "fee_schedule", "disputed_by"),
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
