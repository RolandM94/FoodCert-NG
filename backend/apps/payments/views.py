import csv

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.assessments.models import MedicalAssessment
from apps.employers.models import Employer
from apps.payments.models import ActiveStatus, AssessmentFee, PaymentProvider, PaymentReconciliationRecord, PaymentTransaction, PaymentWebhookEvent, RefundRequest, Receipt
from apps.payments.permissions import can_manage_financial_policy, can_view_national_finance, ensure_employer_billing_access, is_platform_finance_user, is_state_finance_user, scope_payment_transactions_for_user
from apps.payments.serializers import (
    AssessmentFeeSerializer,
    AssessmentPaymentQuoteSerializer,
    BulkAssessmentPaymentQuoteSerializer,
    BulkAssessmentPaymentRequestSerializer,
    ChargebackSerializer,
    InitiateAssessmentPaymentSerializer,
    InitiateSubscriptionPaymentSerializer,
    PaymentProviderSerializer,
    PaymentReconciliationRecordSerializer,
    PaymentTransactionSerializer,
    PaymentWebhookEventSerializer,
    PaymentWebhookSerializer,
    ProviderPerformanceSerializer,
    ReconciliationImportSerializer,
    ReconciliationResolveSerializer,
    RefundRequestCreateSerializer,
    RefundReviewSerializer,
    RefundRequestSerializer,
    ReceiptSerializer,
)
from apps.payments.services import PaymentReconciliationService, PaymentService
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
        if not can_manage_financial_policy(user):
            raise PermissionDenied("Only federal and state admins can configure assessment fees.")
        if user.role == UserRole.STATE_ADMIN and serializer.validated_data["state"] != user.state:
            raise PermissionDenied("State admins can only configure fees for their state.")
        self._validate_fee_split(serializer.validated_data)
        if serializer.validated_data.get("status") in {ActiveStatus.ACTIVE, ActiveStatus.SCHEDULED}:
            self._validate_no_overlap(
                facility_type=serializer.validated_data["facility_type"],
                state=serializer.validated_data["state"],
                effective_from=serializer.validated_data["effective_from"],
                effective_to=serializer.validated_data.get("effective_to"),
            )
        fee = serializer.save(created_by=user)
        log_action(action=AuditAction.CREATE, actor=user, target=fee)

    def perform_update(self, serializer):
        user = self.request.user
        if not can_manage_financial_policy(user):
            raise PermissionDenied("Only federal and state admins can update assessment fees.")
        instance = self.get_object()
        target_state = serializer.validated_data.get("state", instance.state)
        if user.role == UserRole.STATE_ADMIN and target_state != user.state:
            raise PermissionDenied("State admins can only update fees for their state.")
        validated = {
            "amount": serializer.validated_data.get("amount", instance.amount),
            "state_fee": serializer.validated_data.get("state_fee", instance.state_fee),
            "facility_fee": serializer.validated_data.get("facility_fee", instance.facility_fee),
        }
        self._validate_fee_split(validated)
        self._validate_not_used_for_financial_change(instance, serializer.validated_data)
        status_value = serializer.validated_data.get("status", instance.status)
        if status_value in {ActiveStatus.ACTIVE, ActiveStatus.SCHEDULED}:
            self._validate_no_overlap(
                facility_type=serializer.validated_data.get("facility_type", instance.facility_type),
                state=target_state,
                effective_from=serializer.validated_data.get("effective_from", instance.effective_from),
                effective_to=serializer.validated_data.get("effective_to", instance.effective_to),
                exclude=instance,
            )
        fee = serializer.save()
        log_action(action=AuditAction.UPDATE, actor=user, target=fee)

    def _validate_fee_split(self, data):
        total = data["state_fee"] + data["facility_fee"]
        if total != data["amount"]:
            raise ValidationError("State and facility fees must equal the state assessment amount. Platform fees are configured by the platform owner and added at checkout.")

    def _validate_no_overlap(self, *, facility_type, state, effective_from, effective_to=None, exclude=None):
        queryset = AssessmentFee.objects.filter(
            state=state,
            facility_type=facility_type,
            status__in=[ActiveStatus.ACTIVE, ActiveStatus.SCHEDULED],
        )
        if exclude:
            queryset = queryset.exclude(pk=exclude.pk)
        if effective_to is None:
            overlap = queryset.filter(Q(effective_to__isnull=True) | Q(effective_to__gte=effective_from))
        else:
            overlap = queryset.filter(effective_from__lte=effective_to).filter(
                Q(effective_to__isnull=True) | Q(effective_to__gte=effective_from)
            )
        if overlap.exists():
            raise ValidationError("Active or scheduled fee periods cannot overlap for the same state and facility type.")

    def _validate_not_used_for_financial_change(self, instance, data):
        financial_fields = {
            "state",
            "facility_type",
            "amount",
            "currency",
            "state_fee",
            "facility_fee",
            "provider_fee_handling",
            "effective_from",
            "effective_to",
        }
        if not financial_fields.intersection(data):
            return
        if PaymentTransaction.objects.filter(metadata__assessment_fee_id=str(instance.id)).exists():
            raise ValidationError("Fee schedules used by payments cannot be edited. Create a replacement schedule instead.")

    def _ensure_state_or_platform_fee_admin(self, request, fee):
        if not can_manage_financial_policy(request.user):
            raise PermissionDenied("You cannot manage assessment fee schedules.")
        if request.user.role == UserRole.STATE_ADMIN and fee.state_id != request.user.state_id:
            raise PermissionDenied("State admins can only manage fees for their state.")

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        fee = self.get_object()
        self._ensure_state_or_platform_fee_admin(request, fee)
        if fee.status not in {ActiveStatus.DRAFT, ActiveStatus.INACTIVE}:
            raise ValidationError("Only draft or inactive fee schedules can be submitted.")
        fee.status = ActiveStatus.PENDING_APPROVAL
        fee.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=request.user, target=fee, metadata={"event": "fee_schedule_submitted"})
        return Response(self.get_serializer(fee).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        fee = self.get_object()
        self._ensure_state_or_platform_fee_admin(request, fee)
        target_status = ActiveStatus.ACTIVE if fee.effective_from <= timezone.localdate() else ActiveStatus.SCHEDULED
        self._validate_no_overlap(
            facility_type=fee.facility_type,
            state=fee.state,
            effective_from=fee.effective_from,
            effective_to=fee.effective_to,
            exclude=fee,
        )
        fee.status = target_status
        fee.approved_by = request.user
        fee.approved_at = timezone.now()
        fee.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=request.user, target=fee, metadata={"event": "fee_schedule_approved", "status": target_status})
        return Response(self.get_serializer(fee).data)

    @action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        fee = self.get_object()
        self._ensure_state_or_platform_fee_admin(request, fee)
        fee.status = ActiveStatus.SUSPENDED
        fee.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=request.user, target=fee, metadata={"event": "fee_schedule_suspended"})
        return Response(self.get_serializer(fee).data)


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
        return scope_payment_transactions_for_user(self.queryset, user)


class PaymentProviderViewSet(viewsets.ModelViewSet):
    queryset = PaymentProvider.objects.order_by("name")
    serializer_class = PaymentProviderSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["code", "environment", "is_active"]
    ordering_fields = ["name", "created_at", "updated_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        if not is_platform_finance_user(self.request.user):
            raise PermissionDenied("Only platform finance users can manage payment providers.")
        return self.queryset

    def perform_create(self, serializer):
        if not is_platform_finance_user(self.request.user):
            raise PermissionDenied("Only platform finance users can manage payment providers.")
        provider = serializer.save(created_by=self.request.user)
        log_action(action=AuditAction.CREATE, actor=self.request.user, target=provider)

    def perform_update(self, serializer):
        if not is_platform_finance_user(self.request.user):
            raise PermissionDenied("Only platform finance users can manage payment providers.")
        provider = serializer.save()
        log_action(action=AuditAction.UPDATE, actor=self.request.user, target=provider)


class PaymentWebhookEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentWebhookEvent.objects.select_related("provider").order_by("-created_at")
    serializer_class = PaymentWebhookEventSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["provider_code", "event_type", "processing_status", "signature_valid"]
    ordering_fields = ["created_at", "processed_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        if not is_platform_finance_user(self.request.user):
            raise PermissionDenied("Only platform finance users can view payment webhook events.")
        return self.queryset


class PaymentReconciliationRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentReconciliationRecord.objects.select_related("payment_transaction", "resolved_by").order_by("-created_at")
    serializer_class = PaymentReconciliationRecordSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["provider_code", "status", "currency"]
    ordering_fields = ["created_at", "amount", "resolved_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        user = self.request.user
        if is_platform_finance_user(user) or can_view_national_finance(user):
            return self.queryset
        if is_state_finance_user(user) and user.state_id:
            state_id = str(user.state_id)
            return self.queryset.filter(
                Q(payment_transaction__metadata__state_id=state_id)
                | Q(provider_payload__state_id=state_id)
            )
        raise PermissionDenied("Only finance users can view payment reconciliation.")

    def _ensure_import_access(self):
        if not is_platform_finance_user(self.request.user):
            raise PermissionDenied("Only platform finance users can import provider reconciliation records.")

    def _ensure_resolve_access(self):
        if not (is_platform_finance_user(self.request.user) or is_state_finance_user(self.request.user)):
            raise PermissionDenied("Only finance users can resolve reconciliation issues.")

    @extend_schema(request=ReconciliationImportSerializer, responses=PaymentReconciliationRecordSerializer(many=True))
    @action(detail=False, methods=["post"], url_path="import")
    def import_records(self, request):
        self._ensure_import_access()
        serializer = ReconciliationImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            records = PaymentReconciliationService.import_provider_records(
                provider_code=serializer.validated_data["provider_code"],
                records=serializer.validated_data["records"],
                actor=request.user,
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(PaymentReconciliationRecordSerializer(records, many=True).data, status=201)

    @extend_schema(request=ReconciliationResolveSerializer, responses=PaymentReconciliationRecordSerializer)
    @action(detail=True, methods=["post"], url_path="resolve")
    def resolve(self, request, pk=None):
        self._ensure_resolve_access()
        serializer = ReconciliationResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            reconciliation = PaymentReconciliationService.resolve(
                reconciliation=self.get_object(),
                actor=request.user,
                notes=serializer.validated_data["notes"],
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(PaymentReconciliationRecordSerializer(reconciliation).data)

    @extend_schema(responses=ProviderPerformanceSerializer(many=True))
    @action(detail=False, methods=["get"], url_path="provider-performance")
    def provider_performance(self, request):
        rows = PaymentReconciliationService.provider_performance(self.filter_queryset(self.get_queryset()))
        return Response(ProviderPerformanceSerializer(rows, many=True).data)

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="payment-reconciliation.csv"'
        writer = csv.writer(response)
        writer.writerow(["provider_code", "provider_reference", "internal_reference", "amount", "currency", "status", "created_at", "resolved_at"])
        for record in self.filter_queryset(self.get_queryset()):
            writer.writerow([
                record.provider_code,
                record.provider_reference,
                record.internal_reference,
                record.amount,
                record.currency,
                record.status,
                record.created_at.isoformat(),
                record.resolved_at.isoformat() if record.resolved_at else "",
            ])
        return response


class RefundRequestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RefundRequest.objects.select_related("payment_transaction", "payment_allocation", "requested_by", "approved_by").order_by("-created_at")
    serializer_class = RefundRequestSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    filterset_fields = ["status", "payment_transaction"]
    ordering_fields = ["created_at", "amount", "processed_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        if is_platform_finance_user(self.request.user):
            return self.queryset
        return self.queryset.filter(payment_transaction__in=scope_payment_transactions_for_user(PaymentTransaction.objects.all(), self.request.user))

    def _ensure_finance(self):
        if not is_platform_finance_user(self.request.user):
            raise PermissionDenied("Only platform finance users can review refunds.")

    @extend_schema(request=RefundReviewSerializer, responses=RefundRequestSerializer)
    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        self._ensure_finance()
        serializer = RefundReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refund = PaymentService.approve_refund(
                refund_request=self.get_object(),
                actor=request.user,
                notes=serializer.validated_data.get("notes", ""),
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(RefundRequestSerializer(refund).data)

    @extend_schema(request=RefundReviewSerializer, responses=RefundRequestSerializer)
    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        self._ensure_finance()
        serializer = RefundReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refund = PaymentService.reject_refund(
                refund_request=self.get_object(),
                actor=request.user,
                notes=serializer.validated_data.get("notes", ""),
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(RefundRequestSerializer(refund).data)

    @action(detail=True, methods=["post"], url_path="process")
    def process(self, request, pk=None):
        self._ensure_finance()
        try:
            refund = PaymentService.process_refund(refund_request=self.get_object(), actor=request.user)
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(RefundRequestSerializer(refund).data)


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


class AssessmentPaymentAccessMixin:
    def get_assessment(self, request, assessment_id):
        assessment = get_object_or_404(
            MedicalAssessment.objects.select_related("food_handler", "food_handler__user", "employer", "facility", "facility__state", "payment_transaction"),
            id=assessment_id,
        )
        user = request.user
        if user.role == UserRole.SUPER_ADMIN:
            return assessment
        if user.role == UserRole.STATE_ADMIN and assessment.facility.state_id == user.state_id:
            return assessment
        if user.role == UserRole.FOOD_HANDLER and assessment.food_handler.user_id == user.id:
            return assessment
        if user.role == UserRole.EMPLOYER and assessment.employer and assessment.employer.user_id == user.id:
            return assessment
        if user.organization_id and assessment.facility.organization_id == user.organization_id:
            return assessment
        raise PermissionDenied("You cannot access payment details for this assessment.")


class AssessmentPaymentQuoteView(AssessmentPaymentAccessMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=AssessmentPaymentQuoteSerializer)
    def get(self, request, assessment_id):
        assessment = self.get_assessment(request, assessment_id)
        try:
            quote = PaymentService.assessment_payment_quote(assessment=assessment)
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(AssessmentPaymentQuoteSerializer(quote).data)


class AssessmentPaymentInitializeView(AssessmentPaymentAccessMixin, APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses={201: PaymentTransactionSerializer})
    def post(self, request, assessment_id):
        assessment = self.get_assessment(request, assessment_id)
        if request.user.role == UserRole.FOOD_HANDLER and assessment.food_handler.user_id != request.user.id:
            raise PermissionDenied("You can only pay for your own assessment.")
        try:
            transaction_obj = PaymentService.initiate_assessment_payment_for_assessment(
                payer_user=request.user,
                assessment=assessment,
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(PaymentTransactionSerializer(transaction_obj).data, status=201)


class EmployerBulkAssessmentPaymentQuoteView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=BulkAssessmentPaymentRequestSerializer, responses=BulkAssessmentPaymentQuoteSerializer)
    def post(self, request, employer_id):
        employer = get_object_or_404(Employer, id=employer_id)
        ensure_employer_billing_access(request.user, employer, manage=True)
        serializer = BulkAssessmentPaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            quote = PaymentService.bulk_assessment_payment_quote(
                employer=employer,
                assessment_ids=serializer.validated_data["assessment_ids"],
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(BulkAssessmentPaymentQuoteSerializer(quote).data)


class EmployerBulkAssessmentPaymentInitializeView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=BulkAssessmentPaymentRequestSerializer, responses={201: PaymentTransactionSerializer})
    def post(self, request, employer_id):
        employer = get_object_or_404(Employer, id=employer_id)
        ensure_employer_billing_access(request.user, employer, manage=True)
        serializer = BulkAssessmentPaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            transaction_obj = PaymentService.initiate_bulk_assessment_payment(
                payer_user=request.user,
                employer=employer,
                assessment_ids=serializer.validated_data["assessment_ids"],
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
        ensure_employer_billing_access(request.user, employer, manage=True)
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


class PaymentReceiptView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=ReceiptSerializer)
    def get(self, request, transaction_id):
        transaction_obj = get_object_or_404(scope_payment_transactions_for_user(PaymentTransaction.objects.all(), request.user), id=transaction_id)
        if transaction_obj.status != "success":
            raise ValidationError("Receipt is only available after successful payment.")
        receipt = PaymentService.receipt_for_payment(transaction_obj=transaction_obj)
        return Response(ReceiptSerializer(receipt).data)


class PaymentRefundRequestView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=RefundRequestCreateSerializer, responses={201: RefundRequestSerializer})
    def post(self, request, transaction_id):
        transaction_obj = get_object_or_404(scope_payment_transactions_for_user(PaymentTransaction.objects.all(), request.user), id=transaction_id)
        serializer = RefundRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refund = PaymentService.request_refund(
                transaction_obj=transaction_obj,
                actor=request.user,
                reason=serializer.validated_data["reason"],
                amount=serializer.validated_data.get("amount"),
                payment_allocation=serializer.validated_data.get("payment_allocation"),
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(RefundRequestSerializer(refund).data, status=201)


class PaymentRefundRequestListView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(responses=RefundRequestSerializer(many=True))
    def get(self, request, transaction_id):
        transaction_obj = get_object_or_404(scope_payment_transactions_for_user(PaymentTransaction.objects.all(), request.user), id=transaction_id)
        refunds = RefundRequest.objects.filter(payment_transaction=transaction_obj).order_by("-created_at")
        return Response(RefundRequestSerializer(refunds, many=True).data)


class PaymentChargebackView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    @extend_schema(request=ChargebackSerializer, responses=RefundRequestSerializer)
    def post(self, request):
        if not is_platform_finance_user(request.user):
            raise PermissionDenied("Only platform finance users can record chargebacks.")
        serializer = ChargebackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction_obj = get_object_or_404(PaymentTransaction, internal_reference=serializer.validated_data["reference"])
        try:
            refund = PaymentService.record_chargeback(
                transaction_obj=transaction_obj,
                actor=request.user,
                amount=serializer.validated_data.get("amount"),
                reason=serializer.validated_data.get("reason") or "Provider chargeback",
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(RefundRequestSerializer(refund).data, status=201)


class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=PaymentWebhookSerializer, responses=PaymentTransactionSerializer)
    def post(self, request, provider_code=None):
        body = request.body
        serializer = PaymentWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            transaction_obj, _webhook_event = PaymentService.process_webhook(
                provider_code=provider_code,
                payload=serializer.validated_data,
                body=body,
                signature=request.headers.get("X-FoodCert-Signature", ""),
            )
        except PermissionError as exc:
            raise PermissionDenied(str(exc))
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(PaymentTransactionSerializer(transaction_obj).data)
