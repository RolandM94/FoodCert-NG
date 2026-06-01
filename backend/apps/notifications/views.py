from django.db import models as db_models
from django.utils import timezone
from rest_framework import serializers as drf_serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from django.contrib.auth import get_user_model

User = get_user_model()
from apps.notifications.models import (
    BroadcastMessage,
    BroadcastStatus,
    DeliveryStatus,
    Notification,
    NotificationCategory,
    NotificationChannel,
    NotificationDelivery,
    NotificationPreference,
    NotificationPriority,
    NotificationProvider,
    NotificationTemplate,
    TemplateStatus,
)
from apps.notifications.serializers import (
    BroadcastCreateSerializer,
    BroadcastMessageSerializer,
    BroadcastUpdateSerializer,
    BulkPreferenceUpdateSerializer,
    DeliveryRetrySerializer,
    MarkAllReadSerializer,
    NotificationDeliverySerializer,
    NotificationListSerializer,
    NotificationPreferenceSerializer,
    NotificationPreferenceUpdateSerializer,
    NotificationProviderCreateSerializer,
    NotificationProviderSerializer,
    NotificationProviderUpdateSerializer,
    NotificationSerializer,
    NotificationTemplateCreateSerializer,
    NotificationTemplateSerializer,
    NotificationTemplateUpdateSerializer,
    ProviderTestSerializer,
    TemplateApproveSerializer,
    TemplatePreviewSerializer,
    TemplateSubmitSerializer,
    UnreadCountSerializer,
)
from apps.notifications.services import (
    BaseNotificationProvider,
    DeliveryService,
    NotificationService,
    PROVIDER_REGISTRY,
    ProviderSendError,
    RecipientResolver,
    TemplateRenderer,
)

MANDATORY_CATEGORIES = {
    NotificationCategory.SECURITY,
    NotificationCategory.ENFORCEMENT,
}


class NotificationViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "head", "options"]
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        user = self.request.user
        qs = Notification.objects.select_related(
            "recipient", "organization", "organization_unit"
        ).order_by("-created_at")

        if user.role == UserRole.SUPER_ADMIN:
            return qs
        if user.role in (UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN, UserRole.INSPECTOR):
            return qs.filter(recipient=user)
        if user.organization_id:
            return qs.filter(
                db_models.Q(recipient=user) | db_models.Q(organization_id=user.organization_id)
            ).distinct()
        return qs.filter(recipient=user)

    def get_serializer_class(self):
        if self.action == "list":
            return NotificationListSerializer
        if self.action == "unread_count":
            return UnreadCountSerializer
        if self.action == "mark_all_read":
            return MarkAllReadSerializer
        return NotificationSerializer

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        category = self.request.query_params.getlist("category")
        priority = self.request.query_params.getlist("priority")
        is_read = self.request.query_params.get("is_read")
        is_archived = self.request.query_params.get("is_archived")
        search = self.request.query_params.get("search", "").strip()

        if category:
            qs = qs.filter(category__in=category)
        if priority:
            qs = qs.filter(priority__in=priority)
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() == "true")
        if is_archived is not None:
            qs = qs.filter(is_archived=is_archived.lower() == "true")
        if search:
            qs = qs.filter(
                db_models.Q(title__icontains=search) | db_models.Q(message__icontains=search)
            )
        return qs

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        count = self.filter_queryset(self.get_queryset()).filter(is_read=False).count()
        return Response({"unread_count": count})

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at", "updated_at"])
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qs = self.filter_queryset(self.get_queryset()).filter(is_read=False)
        category = serializer.validated_data.get("category")
        if category:
            qs = qs.filter(category=category)
        now = timezone.now()
        qs.update(is_read=True, read_at=now)
        return Response({"marked_read": qs.count()})

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        notification = self.get_object()
        notification.is_archived = True
        notification.save(update_fields=["is_archived", "updated_at"])
        return Response(NotificationSerializer(notification).data)

    @action(detail=True, methods=["post"], url_path="unarchive")
    def unarchive(self, request, pk=None):
        notification = self.get_object()
        notification.is_archived = False
        notification.save(update_fields=["is_archived", "updated_at"])
        return Response(NotificationSerializer(notification).data)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "patch", "post", "head", "options"]
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return NotificationPreference.objects.none()
        return NotificationPreference.objects.filter(
            user=self.request.user,
        ).order_by("category", "channel")

    def get_serializer_class(self):
        if self.action == "bulk_update":
            return BulkPreferenceUpdateSerializer
        if self.action in ("partial_update", "update"):
            return NotificationPreferenceUpdateSerializer
        return NotificationPreferenceSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        pref = self.get_object()
        if "is_enabled" in serializer.validated_data and not serializer.validated_data["is_enabled"]:
            if pref.category in MANDATORY_CATEGORIES:
                raise drf_serializers.ValidationError(
                    f"Cannot disable mandatory notification category: {pref.get_category_display()}"
                )
        serializer.save()

    @action(detail=False, methods=["post"], url_path="bulk-update")
    def bulk_update(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        preferences_data = serializer.validated_data["preferences"]
        user = request.user

        updated = []
        for pref_data in preferences_data:
            category = pref_data["category"]
            channel = pref_data["channel"]
            is_enabled = pref_data.get("is_enabled", True)

            if not is_enabled and category in {c.value for c in MANDATORY_CATEGORIES}:
                raise drf_serializers.ValidationError(
                    f"Cannot disable mandatory notification category: {category}"
                )

            pref, _ = NotificationPreference.objects.update_or_create(
                user=user,
                category=category,
                channel=channel,
                defaults={
                    "is_enabled": is_enabled,
                    "digest_enabled": pref_data.get("digest_enabled", False),
                    "quiet_hours_start": pref_data.get("quiet_hours_start"),
                    "quiet_hours_end": pref_data.get("quiet_hours_end"),
                },
            )
            updated.append(NotificationPreferenceSerializer(pref).data)

        return Response(updated)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return NotificationTemplate.objects.none()
        qs = NotificationTemplate.objects.select_related("state", "created_by", "approved_by").order_by("template_key", "-version")
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return qs
        if user.role == UserRole.STATE_ADMIN and user.state_id:
            return qs.filter(
                db_models.Q(scope="system") | db_models.Q(scope="state", state_id=user.state_id)
            )
        return qs.filter(scope="system")

    def get_serializer_class(self):
        if self.action == "create":
            return NotificationTemplateCreateSerializer
        if self.action in ("partial_update", "update"):
            return NotificationTemplateUpdateSerializer
        if self.action == "preview":
            return TemplatePreviewSerializer
        if self.action == "submit_for_approval":
            return TemplateSubmitSerializer
        if self.action == "approve":
            return TemplateApproveSerializer
        return NotificationTemplateSerializer

    def _require_admin(self):
        if self.request.user.role not in (UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN):
            raise drf_serializers.ValidationError("Only administrators can manage templates.")

    def perform_create(self, serializer):
        self._require_admin()
        serializer.save(created_by=self.request.user, status=TemplateStatus.DRAFT, version=1)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output_serializer = NotificationTemplateSerializer(serializer.instance)
        return Response(output_serializer.data, status=201)

    def perform_update(self, serializer):
        self._require_admin()
        template = self.get_object()
        if template.status == TemplateStatus.ACTIVE:
            new_version = NotificationTemplate.objects.create(
                template_key=template.template_key,
                name=serializer.validated_data.get("name", template.name),
                category=serializer.validated_data.get("category", template.category),
                channel=serializer.validated_data.get("channel", template.channel),
                subject=serializer.validated_data.get("subject", template.subject),
                body=serializer.validated_data.get("body", template.body),
                allowed_variables=serializer.validated_data.get("allowed_variables", template.allowed_variables),
                language=serializer.validated_data.get("language", template.language),
                scope=serializer.validated_data.get("scope", template.scope),
                state=serializer.validated_data.get("state", template.state),
                version=template.version + 1,
                status=TemplateStatus.DRAFT,
                created_by=self.request.user,
            )
            serializer.instance = new_version
        else:
            serializer.save()

    @action(detail=True, methods=["post"], url_path="submit-for-approval")
    def submit_for_approval(self, request, pk=None):
        self._require_admin()
        template = self.get_object()
        if template.status != TemplateStatus.DRAFT:
            raise drf_serializers.ValidationError("Only draft templates can be submitted for approval.")
        template.status = TemplateStatus.PENDING_APPROVAL
        template.save(update_fields=["status", "updated_at"])
        return Response(NotificationTemplateSerializer(template).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        if request.user.role not in (UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN):
            raise drf_serializers.ValidationError("Only super admin or federal admin can approve templates.")
        template = self.get_object()
        if template.status != TemplateStatus.PENDING_APPROVAL:
            raise drf_serializers.ValidationError("Only pending templates can be approved.")
        # Deactivate other versions of same template_key+channel+language
        NotificationTemplate.objects.filter(
            template_key=template.template_key,
            channel=template.channel,
            language=template.language,
            status=TemplateStatus.ACTIVE,
        ).update(status=TemplateStatus.ARCHIVED)
        template.status = TemplateStatus.ACTIVE
        template.approved_by = request.user
        template.approved_at = timezone.now()
        template.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        return Response(NotificationTemplateSerializer(template).data)

    @action(detail=True, methods=["post"], url_path="archive")
    def archive_template(self, request, pk=None):
        self._require_admin()
        template = self.get_object()
        if template.status == TemplateStatus.ARCHIVED:
            raise drf_serializers.ValidationError("Template is already archived.")
        template.status = TemplateStatus.ARCHIVED
        template.save(update_fields=["status", "updated_at"])
        return Response(NotificationTemplateSerializer(template).data)

    @action(detail=True, methods=["post"], url_path="preview")
    def preview(self, request, pk=None):
        template = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        context = serializer.validated_data.get("context", {})
        try:
            result = TemplateRenderer.preview(template=template, context=context)
            return Response(result)
        except Exception as exc:
            raise drf_serializers.ValidationError(str(exc))


class NotificationProviderViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return NotificationProvider.objects.none()
        return NotificationProvider.objects.order_by("priority_order", "name")

    def get_serializer_class(self):
        if self.action == "create":
            return NotificationProviderCreateSerializer
        if self.action in ("partial_update", "update"):
            return NotificationProviderUpdateSerializer
        if self.action == "test":
            return ProviderTestSerializer
        return NotificationProviderSerializer

    def _require_admin(self):
        if self.request.user.role != UserRole.SUPER_ADMIN:
            raise drf_serializers.ValidationError("Only super admin can manage providers.")

    def perform_create(self, serializer):
        self._require_admin()
        if serializer.validated_data.get("is_default"):
            NotificationProvider.objects.filter(
                channel=serializer.validated_data["channel"]
            ).update(is_default=False)
        serializer.save()

    def perform_update(self, serializer):
        self._require_admin()
        provider = self.get_object()
        if serializer.validated_data.get("is_default") and not provider.is_default:
            NotificationProvider.objects.filter(channel=provider.channel).update(is_default=False)
        serializer.save()

    @action(detail=True, methods=["post"], url_path="test")
    def test(self, request, pk=None):
        self._require_admin()
        provider = self.get_object()
        provider_cls = PROVIDER_REGISTRY.get(provider.channel)
        if not provider_cls:
            raise drf_serializers.ValidationError(f"No implementation registered for channel: {provider.channel}")
        try:
            instance = provider_cls(provider)
            ok = instance.test_connection()
            return Response({"success": ok, "channel": provider.channel, "provider": provider.name})
        except Exception as exc:
            return Response({"success": False, "channel": provider.channel, "error": str(exc)})

    @action(detail=True, methods=["post"], url_path="set-default")
    def set_default(self, request, pk=None):
        self._require_admin()
        provider = self.get_object()
        NotificationProvider.objects.filter(channel=provider.channel).update(is_default=False)
        provider.is_default = True
        provider.save(update_fields=["is_default", "updated_at"])
        return Response(NotificationProviderSerializer(provider).data)


# ---- Delivery Tracking ----

RETRY_BACKOFF_MINUTES = [5, 30, 120]  # 5 min, 30 min, 2 hours
MAX_RETRIES = 3


class NotificationDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    http_method_names = ["get", "post", "head", "options"]
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return NotificationDelivery.objects.none()
        return NotificationDelivery.objects.select_related("notification").order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "retry":
            return DeliveryRetrySerializer
        return NotificationDeliverySerializer

    @action(detail=True, methods=["post"], url_path="retry")
    def retry(self, request, pk=None):
        delivery = self.get_object()
        if delivery.status not in (DeliveryStatus.FAILED, DeliveryStatus.BOUNCED):
            raise drf_serializers.ValidationError(f"Cannot retry delivery with status: {delivery.status}")

        if delivery.retry_count >= MAX_RETRIES:
            delivery.status = DeliveryStatus.FAILED
            delivery.error_message = (delivery.error_message or "") + " | Max retries exceeded."
            delivery.save(update_fields=["status", "error_message", "updated_at"])
            raise drf_serializers.ValidationError("Max retries reached. Delivery permanently failed.")

        try:
            result = DeliveryService.dispatch(
                channel=delivery.channel,
                destination=delivery.destination,
                subject=delivery.notification.title,
                body=delivery.notification.message,
            )
            delivery.status = DeliveryStatus.SENT
            delivery.provider_response = result
            delivery.sent_at = timezone.now()
            delivery.retry_count += 1
            delivery.next_retry_at = None
            delivery.error_message = ""
            delivery.save(update_fields=["status", "provider_response", "sent_at", "retry_count", "next_retry_at", "error_message", "updated_at"])
        except ProviderSendError as exc:
            delivery.retry_count += 1
            delivery.error_message = str(exc)
            retry_idx = min(delivery.retry_count - 1, len(RETRY_BACKOFF_MINUTES) - 1)
            delivery.next_retry_at = timezone.now() + timezone.timedelta(minutes=RETRY_BACKOFF_MINUTES[retry_idx])
            if delivery.retry_count >= MAX_RETRIES:
                delivery.status = DeliveryStatus.FAILED
                delivery.next_retry_at = None
            delivery.save(update_fields=["status", "retry_count", "next_retry_at", "error_message", "updated_at"])

        return Response(NotificationDeliverySerializer(delivery).data)


# ---- Broadcast Messaging ----

AUDIENCE_TYPES = {
    "all_users_in_state": "All users in a state",
    "all_employers_in_state": "All employers in a state",
    "all_facilities_in_state": "All facilities in a state",
    "all_inspectors_in_state": "All inspectors in a state",
    "all_state_ministry": "All State Ministry users",
    "all_federal_ministry": "All Federal Ministry users",
    "all_users_in_organization": "All users in an organization",
    "all_users_in_unit": "All users in an organization unit",
    "expiring_certs": "Food handlers with expiring certificates",
}


class BroadcastViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return BroadcastMessage.objects.none()
        return BroadcastMessage.objects.select_related("created_by", "approved_by").order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return BroadcastCreateSerializer
        if self.action in ("partial_update", "update"):
            return BroadcastUpdateSerializer
        return BroadcastMessageSerializer

    def _require_admin(self):
        role = self.request.user.role
        if role not in (UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN):
            raise drf_serializers.ValidationError("Only administrators can manage broadcasts.")

    def perform_create(self, serializer):
        self._require_admin()
        serializer.save(created_by=self.request.user, status=BroadcastStatus.DRAFT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = BroadcastMessageSerializer(serializer.instance)
        return Response(output.data, status=201)

    def perform_update(self, serializer):
        self._require_admin()
        broadcast = self.get_object()
        if broadcast.status != BroadcastStatus.DRAFT:
            raise drf_serializers.ValidationError("Only draft broadcasts can be edited.")
        serializer.save()

    def _resolve_audience(self, broadcast) -> int:
        filters = broadcast.audience_filters or {}
        state_id = filters.get("state_id")
        organization_id = filters.get("organization_id")
        unit_id = filters.get("unit_id")

        from apps.accounts.models import UserRole

        qs = User.objects.filter(is_active=True)

        if broadcast.audience_type == "all_users_in_state" and state_id:
            qs = qs.filter(state_id=state_id)
        elif broadcast.audience_type == "all_employers_in_state" and state_id:
            qs = qs.filter(role=UserRole.EMPLOYER, state_id=state_id)
        elif broadcast.audience_type == "all_facilities_in_state" and state_id:
            qs = qs.filter(role=UserRole.FACILITY_ADMIN, state_id=state_id)
        elif broadcast.audience_type == "all_inspectors_in_state" and state_id:
            qs = qs.filter(role=UserRole.INSPECTOR, state_id=state_id)
        elif broadcast.audience_type == "all_state_ministry" and state_id:
            qs = qs.filter(role=UserRole.STATE_ADMIN, state_id=state_id)
        elif broadcast.audience_type == "all_federal_ministry":
            qs = qs.filter(role__in=[UserRole.FEDERAL_ADMIN, UserRole.SUPER_ADMIN])
        elif broadcast.audience_type == "all_users_in_organization" and organization_id:
            qs = qs.filter(organization_id=organization_id)
        elif broadcast.audience_type == "all_users_in_unit" and unit_id:
            qs = qs.filter(unit_id=unit_id)
        elif broadcast.audience_type == "expiring_certs":
            qs = qs.filter(role=UserRole.FOOD_HANDLER)
        else:
            return 0

        return qs.count()

    @action(detail=True, methods=["post"], url_path="estimate-audience")
    def estimate_audience(self, request, pk=None):
        broadcast = self.get_object()
        count = self._resolve_audience(broadcast)
        broadcast.estimated_recipient_count = count
        broadcast.save(update_fields=["estimated_recipient_count", "updated_at"])
        return Response({"estimated_recipient_count": count})

    @action(detail=True, methods=["post"], url_path="preview")
    def preview_broadcast(self, request, pk=None):
        broadcast = self.get_object()
        return Response({
            "title": broadcast.title,
            "message": broadcast.message,
            "channels": broadcast.channels,
            "audience_type": broadcast.audience_type,
            "audience_filters": broadcast.audience_filters,
            "estimated_recipient_count": broadcast.estimated_recipient_count,
        })

    @action(detail=True, methods=["post"], url_path="submit-for-approval")
    def submit_approval(self, request, pk=None):
        self._require_admin()
        broadcast = self.get_object()
        if broadcast.status != BroadcastStatus.DRAFT:
            raise drf_serializers.ValidationError("Only draft broadcasts can be submitted.")
        broadcast.status = BroadcastStatus.PENDING_APPROVAL
        broadcast.save(update_fields=["status", "updated_at"])
        return Response(BroadcastMessageSerializer(broadcast).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve_broadcast(self, request, pk=None):
        if request.user.role not in (UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN):
            raise drf_serializers.ValidationError("Only super/federal admin can approve broadcasts.")
        broadcast = self.get_object()
        if broadcast.status != BroadcastStatus.PENDING_APPROVAL:
            raise drf_serializers.ValidationError("Only pending broadcasts can be approved.")
        broadcast.status = BroadcastStatus.APPROVED
        broadcast.approved_by = request.user
        broadcast.save(update_fields=["status", "approved_by", "updated_at"])
        return Response(BroadcastMessageSerializer(broadcast).data)

    @action(detail=True, methods=["post"], url_path="send")
    def send_broadcast(self, request, pk=None):
        self._require_admin()
        broadcast = self.get_object()
        if broadcast.status != BroadcastStatus.APPROVED:
            raise drf_serializers.ValidationError("Only approved broadcasts can be sent.")
        if broadcast.status == BroadcastStatus.SENT:
            raise drf_serializers.ValidationError("Broadcast already sent.")

        filters = broadcast.audience_filters or {}
        state_id = filters.get("state_id")
        organization_id = filters.get("organization_id")
        unit_id = filters.get("unit_id")

        from apps.accounts.models import UserRole

        qs = User.objects.filter(is_active=True)

        if broadcast.audience_type == "all_users_in_state" and state_id:
            qs = qs.filter(state_id=state_id)
        elif broadcast.audience_type == "all_employers_in_state" and state_id:
            qs = qs.filter(role=UserRole.EMPLOYER, state_id=state_id)
        elif broadcast.audience_type == "all_facilities_in_state" and state_id:
            qs = qs.filter(role=UserRole.FACILITY_ADMIN, state_id=state_id)
        elif broadcast.audience_type == "all_inspectors_in_state" and state_id:
            qs = qs.filter(role=UserRole.INSPECTOR, state_id=state_id)
        elif broadcast.audience_type == "all_state_ministry" and state_id:
            qs = qs.filter(role=UserRole.STATE_ADMIN, state_id=state_id)
        elif broadcast.audience_type == "all_federal_ministry":
            qs = qs.filter(role__in=[UserRole.FEDERAL_ADMIN, UserRole.SUPER_ADMIN])
        elif broadcast.audience_type == "all_users_in_organization" and organization_id:
            qs = qs.filter(organization_id=organization_id)
        elif broadcast.audience_type == "all_users_in_unit" and unit_id:
            qs = qs.filter(unit_id=unit_id)
        elif broadcast.audience_type == "expiring_certs":
            qs = qs.filter(role=UserRole.FOOD_HANDLER)
        else:
            raise drf_serializers.ValidationError(f"Unknown audience type: {broadcast.audience_type}")

        recipients = [
            {
                "user_id": str(u.id),
                "email": u.email or "",
                "phone": u.phone or "",
                "recipient_type": u.role or "",
                "organization_id": str(u.organization_id) if u.organization_id else "",
                "organization_unit_id": str(u.unit_id) if u.unit_id else "",
            }
            for u in qs[:1000]  # batch limit for safety
        ]

        if not recipients:
            raise drf_serializers.ValidationError("No recipients found for this audience.")

        sent = 0
        failed = 0
        for recipient in recipients:
            try:
                NotificationService.send(
                    category=broadcast.category,
                    priority=broadcast.priority,
                    title=broadcast.title,
                    message=broadcast.message,
                    recipients=[recipient],
                    channels=broadcast.channels or [NotificationChannel.IN_APP],
                )
                sent += 1
            except Exception:
                failed += 1

        broadcast.status = BroadcastStatus.SENT
        broadcast.sent_count = sent
        broadcast.failed_count = failed
        broadcast.sent_at = timezone.now()
        broadcast.save(update_fields=["status", "sent_count", "failed_count", "sent_at", "updated_at"])
        return Response(BroadcastMessageSerializer(broadcast).data)


# ---- Webhooks ----


class WebhookPayloadSerializer(drf_serializers.Serializer):
    message_id = drf_serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    event = drf_serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    status = drf_serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    error = drf_serializers.CharField(max_length=500, required=False, allow_blank=True, default="")
    raw = drf_serializers.DictField(required=False, default=dict)


class EmailWebhookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WebhookPayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider_message_id = serializer.validated_data.get("message_id", "")
        event = serializer.validated_data.get("event", "")

        if provider_message_id:
            delivery = NotificationDelivery.objects.filter(
                provider_message_id=provider_message_id,
            ).first()
            if delivery:
                if event == "delivered":
                    delivery.status = DeliveryStatus.DELIVERED
                    delivery.delivered_at = timezone.now()
                elif event == "bounced":
                    delivery.status = DeliveryStatus.BOUNCED
                elif event == "opened":
                    delivery.status = DeliveryStatus.OPENED
                elif event == "clicked":
                    delivery.status = DeliveryStatus.CLICKED
                elif event == "failed":
                    delivery.status = DeliveryStatus.FAILED
                delivery.provider_response = serializer.validated_data.get("raw", {})
                delivery.save(update_fields=["status", "delivered_at", "provider_response", "updated_at"])
                return Response({"acknowledged": True, "delivery_id": str(delivery.id)})

        return Response({"acknowledged": True}, status=200)


class SMSWebhookView(EmailWebhookView):
    pass


class WhatsAppWebhookView(EmailWebhookView):
    pass


# ---- Internal API ----

from apps.notifications.serializers import NotificationSerializer


class EventPayloadSerializer(drf_serializers.Serializer):
    event_key = drf_serializers.CharField(max_length=150)
    source_module = drf_serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    related_object_type = drf_serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    related_object_id = drf_serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    actor_id = drf_serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    organization_id = drf_serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    state_id = drf_serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    payload = drf_serializers.DictField(required=False, default=dict)


class SendPayloadSerializer(drf_serializers.Serializer):
    category = drf_serializers.ChoiceField(choices=NotificationCategory.choices)
    priority = drf_serializers.ChoiceField(choices=NotificationPriority.choices, default=NotificationPriority.NORMAL)
    title = drf_serializers.CharField(max_length=255)
    message = drf_serializers.CharField()
    action_url = drf_serializers.URLField(required=False, allow_blank=True, default="")
    related_object_type = drf_serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    related_object_id = drf_serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    channels = drf_serializers.ListField(child=drf_serializers.CharField(), required=False)
    recipients = drf_serializers.ListField(child=drf_serializers.DictField())


class SendTemplatePayloadSerializer(drf_serializers.Serializer):
    template_key = drf_serializers.CharField(max_length=150)
    context = drf_serializers.DictField()
    channels = drf_serializers.ListField(child=drf_serializers.CharField(), required=False)
    action_url = drf_serializers.URLField(required=False, allow_blank=True, default="")
    related_object_type = drf_serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    related_object_id = drf_serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    recipients = drf_serializers.ListField(child=drf_serializers.DictField(), required=False)


class SchedulePayloadSerializer(drf_serializers.Serializer):
    template_key = drf_serializers.CharField(max_length=150)
    context = drf_serializers.DictField()
    scheduled_at = drf_serializers.DateTimeField()
    source_module = drf_serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    related_object_type = drf_serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    related_object_id = drf_serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    channels = drf_serializers.ListField(child=drf_serializers.CharField(), required=False)
    action_url = drf_serializers.URLField(required=False, allow_blank=True, default="")
    recipients = drf_serializers.ListField(child=drf_serializers.DictField(), required=False)


class InternalEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EventPayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = NotificationService.emit_event(**serializer.validated_data)
        return Response({"event_id": str(event.id), "event_key": event.event_key})


class InternalSendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendPayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notifications = NotificationService.send(**serializer.validated_data)
        return Response(NotificationSerializer(notifications, many=True).data, status=201)


class InternalSendTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendTemplatePayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notifications = NotificationService.send_template(**serializer.validated_data)
        if notifications:
            return Response(NotificationSerializer(notifications, many=True).data, status=201)
        return Response([], status=200)


class InternalScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SchedulePayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = NotificationService.schedule(**serializer.validated_data)
        return Response({"event_id": str(event.id), "scheduled_at": event.scheduled_at}, status=201)


# ---- Dashboard ----

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in (UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN):
            return Response({"detail": "Admin access required."}, status=403)

        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        total_today = Notification.objects.filter(created_at__gte=today).count()
        emails_today = NotificationDelivery.objects.filter(channel="email", sent_at__gte=today).count()
        sms_today = NotificationDelivery.objects.filter(channel="sms", sent_at__gte=today).count()
        whatsapp_today = NotificationDelivery.objects.filter(channel="whatsapp", sent_at__gte=today).count()
        in_app_today = total_today

        total_deliveries = NotificationDelivery.objects.count()
        failed = NotificationDelivery.objects.filter(status__in=["failed", "bounced", "rejected"]).count()
        success_rate = round(((total_deliveries - failed) / total_deliveries * 100) if total_deliveries else 100, 1)

        pending_retries = NotificationDelivery.objects.filter(
            status=DeliveryStatus.FAILED,
            retry_count__lt=3,
            next_retry_at__isnull=False,
        ).count()

        critical_sent = Notification.objects.filter(priority=NotificationPriority.CRITICAL, created_at__gte=today).count()
        broadcasts_sent = BroadcastMessage.objects.filter(status=BroadcastStatus.SENT).count()
        provider_failures = NotificationDelivery.objects.filter(
            status=DeliveryStatus.FAILED,
            created_at__gte=today,
        ).count()

        by_channel = {}
        for channel in NotificationChannel.values:
            by_channel[channel] = NotificationDelivery.objects.filter(channel=channel).count()

        by_category = {}
        for cat in NotificationCategory.values:
            by_category[cat] = Notification.objects.filter(category=cat).count()

        by_status = {}
        for status in DeliveryStatus.values:
            by_status[status] = NotificationDelivery.objects.filter(status=status).count()

        return Response({
            "total_today": total_today,
            "emails_today": emails_today,
            "sms_today": sms_today,
            "whatsapp_today": whatsapp_today,
            "in_app_today": in_app_today,
            "delivery_success_rate": success_rate,
            "failed_deliveries": failed,
            "pending_retries": pending_retries,
            "critical_sent": critical_sent,
            "broadcasts_sent": broadcasts_sent,
            "provider_failures": provider_failures,
            "by_channel": by_channel,
            "by_category": by_category,
            "by_status": by_status,
        })

