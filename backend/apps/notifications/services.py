import re
import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.audit.services import log_action
from apps.notifications.models import (
    DeliveryStatus,
    Notification,
    NotificationCategory,
    NotificationChannel,
    NotificationDelivery,
    NotificationEvent,
    NotificationPreference,
    NotificationPriority,
    NotificationProvider,
    NotificationTemplate,
    TemplateStatus,
)

User = get_user_model()

logger = logging.getLogger(__name__)

VARIABLE_PATTERN = re.compile(r"\{\{\s*(\w+)\s*\}\}")

SENSITIVE_VARIABLES = frozenset({
    "full_nin",
    "lab_results",
    "diagnosis",
    "doctor_notes",
    "health_declaration_answers",
    "treatment_details",
    "payment_card_details",
    "provider_secret_keys",
})


class RenderError(ValueError):
    pass


class TemplateRenderer:

    @classmethod
    def extract_variables(cls, body: str) -> set[str]:
        return set(VARIABLE_PATTERN.findall(body))

    @classmethod
    def render(cls, *, template: NotificationTemplate, context: dict) -> dict:
        if template.status != TemplateStatus.ACTIVE:
            raise RenderError(f"Template '{template.template_key}' is not active (status={template.status}).")

        allowed = set(template.allowed_variables)
        provided = set(context.keys())
        sensitive_present = provided & SENSITIVE_VARIABLES
        if sensitive_present:
            raise RenderError(f"Sensitive variable(s) not allowed in template: {sorted(sensitive_present)}")

        unauthorized = provided - allowed
        if unauthorized:
            raise RenderError(f"Variable(s) not in allowed list for template '{template.template_key}': {sorted(unauthorized)}")

        subject = template.subject
        body = template.body
        for var, value in context.items():
            placeholder = "{{ " + var + " }}"
            str_value = str(value) if value is not None else ""
            subject = subject.replace(placeholder, str_value)
            body = body.replace(placeholder, str_value)

        return {"subject": subject, "body": body}

    @classmethod
    def preview(cls, *, template: NotificationTemplate, context: dict | None = None) -> dict:
        if context is None:
            context = {}
        allowed = set(template.allowed_variables)
        preview_context = {}
        for var in allowed:
            preview_context[var] = context.get(var, f"[{var}]")
        try:
            subject = template.subject
            body = template.body
            for var, value in preview_context.items():
                placeholder = "{{ " + var + " }}"
                str_value = str(value) if value is not None else ""
                subject = subject.replace(placeholder, str_value)
                body = body.replace(placeholder, str_value)
            return {"subject": subject, "body": body}
        except Exception as exc:
            raise RenderError(f"Preview render failed: {exc}")


# ---- Provider Abstraction ----

class ProviderSendError(Exception):
    pass


class BaseNotificationProvider:
    """Abstract provider that all channel providers must implement."""

    channel: str = ""

    def __init__(self, provider: NotificationProvider):
        self.provider = provider

    def send(
        self,
        *,
        destination: str,
        subject: str,
        body: str,
        sender_id: str = "",
    ) -> dict:
        raise NotImplementedError

    def test_connection(self) -> bool:
        raise NotImplementedError

    @classmethod
    def validate_config(cls, config: dict) -> list[str]:
        """Return list of missing required config keys."""
        return []


class InAppProvider(BaseNotificationProvider):
    """In-app delivery is handled by creating Notification records directly.
       This provider is a no-op for external delivery — the notification record
       itself serves as the in-app message."""

    channel = NotificationChannel.IN_APP

    def send(self, *, destination: str, subject: str, body: str, sender_id: str = "") -> dict:
        return {"status": "delivered", "channel": "in_app"}

    def test_connection(self) -> bool:
        return True


class MockEmailProvider(BaseNotificationProvider):
    """Mock email provider that logs to console. Replace with SendGrid/SES/etc. in production."""

    channel = NotificationChannel.EMAIL

    def send(self, *, destination: str, subject: str, body: str, sender_id: str = "") -> dict:
        logger.info(
            "[MOCK EMAIL] to=%s subject=%s body_preview=%s",
            destination,
            subject,
            body[:100],
        )
        return {"status": "sent", "channel": "email", "provider": self.provider.name}

    def test_connection(self) -> bool:
        return True


class MockSMSProvider(BaseNotificationProvider):
    """Mock SMS provider that logs to console. Replace with Termii/Twilio/etc. in production."""

    channel = NotificationChannel.SMS

    def send(self, *, destination: str, subject: str, body: str, sender_id: str = "") -> dict:
        logger.info(
            "[MOCK SMS] to=%s sender=%s body=%s",
            destination,
            sender_id or self.provider.sender_id,
            body[:160],
        )
        return {"status": "sent", "channel": "sms", "provider": self.provider.name}

    def test_connection(self) -> bool:
        return True


class MockWhatsAppProvider(BaseNotificationProvider):
    """Mock WhatsApp provider that logs to console. Replace with Meta API/Twilio/etc. in production."""

    channel = NotificationChannel.WHATSAPP

    def send(self, *, destination: str, subject: str, body: str, sender_id: str = "") -> dict:
        logger.info(
            "[MOCK WHATSAPP] to=%s body=%s",
            destination,
            body[:200],
        )
        return {"status": "sent", "channel": "whatsapp", "provider": self.provider.name}

    def test_connection(self) -> bool:
        return True


PROVIDER_REGISTRY = {
    NotificationChannel.EMAIL: MockEmailProvider,
    NotificationChannel.SMS: MockSMSProvider,
    NotificationChannel.WHATSAPP: MockWhatsAppProvider,
    NotificationChannel.IN_APP: InAppProvider,
}


class DeliveryService:
    """Resolves the appropriate provider and dispatches a message."""

    @classmethod
    def get_provider_for_channel(cls, channel: str) -> NotificationProvider | None:
        return (
            NotificationProvider.objects.filter(
                channel=channel,
                is_active=True,
            )
            .order_by("-is_default", "priority_order")
            .first()
        )

    @classmethod
    def dispatch(cls, *, channel: str, destination: str, subject: str, body: str) -> dict:
        provider = cls.get_provider_for_channel(channel)
        if not provider:
            raise ProviderSendError(f"No active provider configured for channel: {channel}")

        provider_cls = PROVIDER_REGISTRY.get(channel)
        if not provider_cls:
            raise ProviderSendError(f"No provider implementation registered for channel: {channel}")

        instance = provider_cls(provider)
        return instance.send(
            destination=destination,
            subject=subject,
            body=body,
            sender_id=provider.sender_id,
        )


# ---- Recipient Resolution ----

class RecipientResolutionError(Exception):
    pass


class RecipientResolver:
    """Resolves who should receive a notification for a given event.
       Domain-specific resolution rules are added via register()."""

    _handlers: dict[str, callable] = {}

    @classmethod
    def register(cls, event_key: str, handler: callable):
        cls._handlers[event_key] = handler

    @classmethod
    def resolve(cls, *, event_key: str, payload: dict | None = None) -> list[dict]:
        """
        Returns a list of recipient specs:
        [{user_id, email, phone, recipient_type, organization_id, organization_unit_id}, ...]
        """
        handler = cls._handlers.get(event_key)
        if handler:
            return handler(payload or {})

        return []

    @classmethod
    def resolve_user_ids(cls, *, user_ids: list[str] | None = None, role: str | None = None,
                         organization_id: str | None = None, unit_id: str | None = None) -> list[dict]:
        """Utility: resolve recipients by filters."""
        qs = User.objects.filter(is_active=True)
        if user_ids:
            qs = qs.filter(id__in=user_ids)
        if role:
            qs = qs.filter(role=role)
        if organization_id:
            qs = qs.filter(organization_id=organization_id)
        if unit_id:
            qs = qs.filter(unit_id=unit_id)

        return [
            {
                "user_id": str(u.id),
                "email": u.email or "",
                "phone": u.phone or "",
                "recipient_type": u.role or "",
                "organization_id": str(u.organization_id) if u.organization_id else "",
                "organization_unit_id": str(u.unit_id) if u.unit_id else "",
            }
            for u in qs
        ]


# Register default recipient resolution handlers for common events.

def _register_default_handlers():
    from apps.accounts.models import UserRole

    def _certificate_issued(payload: dict) -> list[dict]:
        food_handler_id = payload.get("food_handler_user_id")
        employer_admin_ids = payload.get("employer_admin_ids", [])
        facility_admin_id = payload.get("facility_admin_id")
        all_ids = set()
        if food_handler_id:
            all_ids.add(food_handler_id)
        all_ids.update(employer_admin_ids)
        if facility_admin_id:
            all_ids.add(facility_admin_id)
        return RecipientResolver.resolve_user_ids(user_ids=list(all_ids)) if all_ids else []

    def _certificate_expiring(payload: dict) -> list[dict]:
        food_handler_id = payload.get("food_handler_user_id")
        employer_admin_ids = payload.get("employer_admin_ids", [])
        all_ids = set()
        if food_handler_id:
            all_ids.add(food_handler_id)
        all_ids.update(employer_admin_ids)
        return RecipientResolver.resolve_user_ids(user_ids=list(all_ids)) if all_ids else []

    def _assessment_assigned(payload: dict) -> list[dict]:
        doctor_id = payload.get("doctor_id")
        food_handler_id = payload.get("food_handler_user_id")
        return RecipientResolver.resolve_user_ids(
            user_ids=[uid for uid in [doctor_id, food_handler_id] if uid]
        )

    def _lab_request_created(payload: dict) -> list[dict]:
        facility_org_id = payload.get("facility_organization_id")
        return RecipientResolver.resolve_user_ids(
            role=str(UserRole.LAB_STAFF),
            organization_id=facility_org_id,
        )

    def _inspection_assigned(payload: dict) -> list[dict]:
        inspector_id = payload.get("inspector_id")
        employer_admin_id = payload.get("employer_admin_id")
        return RecipientResolver.resolve_user_ids(
            user_ids=[uid for uid in [inspector_id, employer_admin_id] if uid]
        )

    def _payment_successful(payload: dict) -> list[dict]:
        payer_id = payload.get("payer_id")
        return RecipientResolver.resolve_user_ids(user_ids=[payer_id] if payer_id else [])

    def _enforcement_notice(payload: dict) -> list[dict]:
        employer_admin_id = payload.get("employer_admin_id")
        inspector_coordinator_id = payload.get("inspector_coordinator_id")
        return RecipientResolver.resolve_user_ids(
            user_ids=[uid for uid in [employer_admin_id, inspector_coordinator_id] if uid]
        )

    def _state_report_overdue(payload: dict) -> list[dict]:
        state_id = payload.get("state_id")
        return RecipientResolver.resolve_user_ids(
            role=str(UserRole.STATE_ADMIN),
        )

    handlers = {
        "certificate.issued": _certificate_issued,
        "certificate.expiring_soon": _certificate_expiring,
        "certificate.expired": _certificate_expiring,
        "certificate.suspended": _certificate_expiring,
        "certificate.revoked": _certificate_expiring,
        "assessment.doctor_assigned": _assessment_assigned,
        "assessment.declaration_pending": _assessment_assigned,
        "lab.request_created": _lab_request_created,
        "inspection.assigned": _inspection_assigned,
        "payment.successful": _payment_successful,
        "enforcement.notice_issued": _enforcement_notice,
        "state_report.overdue": _state_report_overdue,
    }

    for event_key, handler in handlers.items():
        RecipientResolver.register(event_key, handler)

_register_default_handlers()


# ---- Preference Service ----

MANDATORY_PRIORITIES = {NotificationPriority.CRITICAL}
MANDATORY_CATEGORIES = {NotificationCategory.SECURITY, NotificationCategory.ENFORCEMENT}


class NotificationPreferenceService:

    @classmethod
    def is_channel_allowed(cls, *, user_id: str, category: str, channel: str, priority: str = NotificationPriority.NORMAL) -> bool:
        if priority in MANDATORY_PRIORITIES or category in {c.value for c in MANDATORY_CATEGORIES}:
            return True

        pref = NotificationPreference.objects.filter(
            user_id=user_id,
            category=category,
            channel=channel,
        ).first()

        if pref is None:
            return True  # default: enabled

        if not pref.is_enabled:
            return False

        if pref.quiet_hours_start and pref.quiet_hours_end:
            now = timezone.localtime().time()
            start = pref.quiet_hours_start
            end = pref.quiet_hours_end
            if start < end:
                if start <= now <= end:
                    return False
            else:
                if now >= start or now <= end:
                    return False

        return True


# ---- Core Notification Service ----

class NotificationService:

    @classmethod
    def notify(cls, *, event_key: str, source_module: str = "",
               recipients: list[dict] | None = None,
               category: str | None = None,
               priority: str = NotificationPriority.NORMAL,
               title: str = "", message: str = "",
               template_key: str | None = None,
               template_context: dict | None = None,
               channels: list[str] | None = None,
               action_url: str = "",
               related_object_type: str = "", related_object_id: str = "",
               actor_id: str | None = None, organization_id: str | None = None,
               state_id: str | None = None,
               payload: dict | None = None) -> list[Notification]:
        """
        One-call convenience: emit event + resolve recipients + send.
        If template_key is provided, renders the template for title/message.
        If recipients not provided, resolves via RecipientResolver.
        """
        cls.emit_event(
            event_key=event_key,
            source_module=source_module,
            related_object_type=related_object_type,
            related_object_id=related_object_id or "",
            actor_id=actor_id,
            organization_id=organization_id,
            state_id=state_id,
            payload=payload or {},
        )

        if recipients is None:
            recipients = RecipientResolver.resolve(
                event_key=event_key,
                payload=payload,
            )

        if template_key and template_context:
            template = NotificationTemplate.objects.filter(
                template_key=template_key,
                status=TemplateStatus.ACTIVE,
            ).order_by("-version").first()
            if template:
                rendered = TemplateRenderer.render(template=template, context=template_context)
                title = rendered["subject"] or title or event_key
                message = rendered["body"] or message

        if recipients:
            return cls.send(
                category=category or NotificationCategory.SYSTEM,
                priority=priority,
                title=title,
                message=message,
                action_url=action_url,
                recipients=recipients,
                channels=channels,
                related_object_type=related_object_type,
                related_object_id=related_object_id or "",
            )
        return []

    @classmethod
    @transaction.atomic
    def emit_event(cls, *, event_key: str, source_module: str = "",
                   related_object_type: str = "", related_object_id: str = "",
                   payload: dict | None = None, actor_id: str | None = None,
                   organization_id: str | None = None, state_id: str | None = None) -> NotificationEvent:
        event = NotificationEvent.objects.create(
            event_key=event_key,
            source_module=source_module or "",
            related_object_type=related_object_type or "",
            related_object_id=related_object_id or None,
            payload=payload or {},
        )
        log_action(
            action="notification_event_emitted",
            target=event,
            metadata={"event_key": event_key, "source_module": source_module},
        )
        return event

    @classmethod
    @transaction.atomic
    def send(cls, *, category: str, priority: str = NotificationPriority.NORMAL,
             title: str, message: str, action_url: str = "",
             recipients: list[dict],
             channels: list[str] | None = None,
             related_object_type: str = "", related_object_id: str = "") -> list[Notification]:
        if channels is None:
            channels = [NotificationChannel.IN_APP]

        notifications = []
        for recipient in recipients:
            user_id = recipient.get("user_id") or None
            org_id = recipient.get("organization_id") or None
            unit_id = recipient.get("organization_unit_id") or None

            notification = Notification.objects.create(
                recipient_id=user_id,
                recipient_email=recipient.get("email", ""),
                recipient_phone=recipient.get("phone", ""),
                recipient_type=recipient.get("recipient_type", ""),
                organization_id=org_id,
                organization_unit_id=unit_id,
                category=category,
                priority=priority,
                title=title,
                message=message,
                action_url=action_url,
                related_object_type=related_object_type or "",
                related_object_id=related_object_id or None,
            )
            notifications.append(notification)

            for channel in channels:
                if channel == NotificationChannel.IN_APP:
                    continue  # already created above

                if user_id and not NotificationPreferenceService.is_channel_allowed(
                    user_id=user_id, category=category, channel=channel, priority=priority,
                ):
                    delivery = NotificationDelivery.objects.create(
                        notification=notification,
                        channel=channel,
                        destination=recipient.get("email") if channel == NotificationChannel.EMAIL else recipient.get("phone", ""),
                        status=DeliveryStatus.CANCELLED,
                        error_message="User preference disabled for this channel",
                    )
                    continue

                destination = recipient.get("email") if channel == NotificationChannel.EMAIL else recipient.get("phone", "")

                delivery = NotificationDelivery.objects.create(
                    notification=notification,
                    channel=channel,
                    destination=destination,
                    status=DeliveryStatus.QUEUED,
                )

                try:
                    result = DeliveryService.dispatch(
                        channel=channel,
                        destination=destination,
                        subject=title,
                        body=message,
                    )
                    delivery.status = DeliveryStatus.SENT
                    delivery.provider_response = result
                    delivery.sent_at = timezone.now()
                    delivery.save(update_fields=["status", "provider_response", "sent_at", "updated_at"])
                except ProviderSendError as exc:
                    delivery.status = DeliveryStatus.FAILED
                    delivery.error_message = str(exc)
                    delivery.save(update_fields=["status", "error_message", "updated_at"])

        log_action(
            action="notification_sent",
            target=notifications[0] if notifications else None,
            metadata={
                "category": category,
                "priority": priority,
                "recipient_count": len(notifications),
                "channels": channels,
            },
        )
        return notifications

    @classmethod
    def send_template(cls, *, template_key: str, context: dict,
                      channels: list[str] | None = None, action_url: str = "",
                      related_object_type: str = "", related_object_id: str = "",
                      override_recipients: list[dict] | None = None,
                      recipients: list[dict] | None = None) -> list[Notification] | None:
        template = NotificationTemplate.objects.filter(
            template_key=template_key,
            status=TemplateStatus.ACTIVE,
        ).order_by("-version").first()

        if not template:
            raise RenderError(f"No active template found for key: {template_key}")

        rendered = TemplateRenderer.render(template=template, context=context)
        title = rendered["subject"] or template_key
        message = rendered["body"]

        if override_recipients:
            recipients = override_recipients
        elif recipients:
            pass
        else:
            event_payload = context.get("_event_payload", {})
            event_key = context.get("_event_key", template_key)
            recipients = RecipientResolver.resolve(event_key=event_key, payload=event_payload)

        if not recipients:
            return None

        return cls.send(
            category=template.category,
            priority=NotificationPriority.NORMAL,
            title=title,
            message=message,
            action_url=action_url,
            recipients=recipients,
            channels=channels or [template.channel],
            related_object_type=related_object_type,
            related_object_id=related_object_id,
        )

    @classmethod
    def schedule(cls, *, template_key: str, context: dict, scheduled_at,
                 source_module: str = "", related_object_type: str = "",
                 related_object_id: str = "", channels: list[str] | None = None,
                 action_url: str = "", recipients_override: list[dict] | None = None) -> NotificationEvent:
        payload = {
            "_template_key": template_key,
            "_context": context,
            "_channels": channels,
            "_action_url": action_url,
            "_recipients": recipients_override,
            "_related_object_type": related_object_type,
            "_related_object_id": related_object_id,
        }
        return NotificationEvent.objects.create(
            event_key=template_key,
            source_module=source_module or "scheduler",
            related_object_type=related_object_type or "",
            related_object_id=related_object_id or None,
            payload=payload,
            scheduled_at=scheduled_at,
        )

    @classmethod
    def process_due_reminders(cls) -> int:
        now = timezone.now()
        events = NotificationEvent.objects.filter(
            processed=False,
            scheduled_at__lte=now,
        ).order_by("scheduled_at")[:50]

        processed_count = 0
        for event in events:
            try:
                p = event.payload
                template_key = p.get("_template_key")
                context = p.get("_context", {})
                channels = p.get("_channels")
                action_url = p.get("_action_url", "")
                related_object_type = p.get("_related_object_type", "")
                related_object_id = p.get("_related_object_id", "")
                recipients = p.get("_recipients")

                if template_key:
                    cls.send_template(
                        template_key=template_key,
                        context=context,
                        channels=channels,
                        action_url=action_url,
                        related_object_type=related_object_type,
                        related_object_id=related_object_id,
                        override_recipients=recipients,
                    )
                event.processed = True
                event.processed_at = now
                event.save(update_fields=["processed", "processed_at"])
                processed_count += 1
            except Exception as exc:
                logger.error("Failed to process reminder event %s: %s", event.id, exc)

        return processed_count


# ---- Digest Service ----

class DigestService:

    @classmethod
    def send_daily_digest(cls) -> int:
        now = timezone.now()
        since = now - timezone.timedelta(hours=24)
        users_with_digest = NotificationPreference.objects.filter(
            digest_enabled=True,
        ).values_list("user_id", flat=True).distinct()

        sent = 0
        for user_id in users_with_digest:
            notifications = Notification.objects.filter(
                recipient_id=user_id,
                created_at__gte=since,
                is_read=False,
            )
            count = notifications.count()
            if count == 0:
                continue

            user = User.objects.filter(id=user_id).first()
            if not user or not user.email:
                continue

            lines = [f"You have {count} unread notification(s) from the last 24 hours:"]
            for n in notifications[:10]:
                lines.append(f"  • {n.title} ({n.get_category_display()})")
            if count > 10:
                lines.append(f"  ... and {count - 10} more")

            try:
                NotificationService.send(
                    category=NotificationCategory.SYSTEM,
                    priority=NotificationPriority.LOW,
                    title="Daily Notification Digest",
                    message="\n".join(lines),
                    recipients=[{
                        "user_id": str(user.id),
                        "email": user.email,
                        "recipient_type": user.role or "",
                    }],
                    channels=[NotificationChannel.EMAIL],
                )
                sent += 1
            except Exception as exc:
                logger.error("Digest send failed for user %s: %s", user_id, exc)

        return sent
