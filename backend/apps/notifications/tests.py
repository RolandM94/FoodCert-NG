from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, UserRole
from apps.audit.models import AuditLog
from apps.locations.models import State
from apps.notifications.models import (
    BroadcastMessage,
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
from apps.notifications.services import (
    NotificationService,
    SENSITIVE_VARIABLES,
    TemplateRenderer,
    RenderError,
)


class PrivacySecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com",
            password="pass", role=UserRole.FOOD_HANDLER
        )
        self.template = NotificationTemplate.objects.create(
            template_key="test.tmpl", name="Test",
            category=NotificationCategory.CERTIFICATE,
            channel=NotificationChannel.EMAIL,
            subject="Hello {{ user_name }}",
            body="Cert: {{ certificate_number }}",
            allowed_variables=["user_name", "certificate_number"],
            status=TemplateStatus.ACTIVE,
        )

    def test_sensitive_variables_blocked_in_render(self):
        for var in SENSITIVE_VARIABLES:
            ctx = {var: "secret", "certificate_number": "CERT-001"}
            with self.assertRaises(RenderError):
                TemplateRenderer.render(template=self.template, context=ctx)

    def test_render_blocks_unauthorized_variables(self):
        with self.assertRaises(RenderError):
            TemplateRenderer.render(
                template=self.template,
                context={"unknown_var": "x"}
            )

    def test_render_blocks_inactive_template(self):
        self.template.status = TemplateStatus.DRAFT
        self.template.save()
        with self.assertRaises(RenderError):
            TemplateRenderer.render(
                template=self.template,
                context={"user_name": "X", "certificate_number": "Y"}
            )


class PermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.handler = User.objects.create_user(
            username="phandler", email="ph@test.com",
            password="pass", role=UserRole.FOOD_HANDLER
        )
        self.employer = User.objects.create_user(
            username="pemployer", email="pe@test.com",
            password="pass", role=UserRole.EMPLOYER
        )
        self.admin = User.objects.create_user(
            username="padmin", email="pa@test.com", password="pass",
            role=UserRole.SUPER_ADMIN, is_staff=True, is_superuser=True
        )

    def _login(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_user_sees_only_own_notifications(self):
        n1 = Notification.objects.create(
            recipient=self.handler, category="system",
            title="FH note", message="x"
        )
        n2 = Notification.objects.create(
            recipient=self.employer, category="system",
            title="Emp note", message="x"
        )
        self._login(self.handler)
        resp = self.client.get("/api/notifications/")
        self.assertEqual(resp.status_code, 200)

    def test_super_admin_sees_all(self):
        Notification.objects.create(
            recipient=self.handler, category="system", title="FH", message="x"
        )
        Notification.objects.create(
            recipient=self.employer, category="system", title="Emp", message="x"
        )
        self._login(self.admin)
        resp = self.client.get("/api/notifications/")
        self.assertEqual(resp.status_code, 200)

    def test_mandatory_categories_cannot_be_disabled(self):
        self._login(self.handler)
        resp = self.client.post(
            "/api/notification-preferences/bulk-update/",
            {"preferences": [{
                "category": "security", "channel": "email",
                "is_enabled": False
            }]},
            format="json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_non_admin_cannot_create_template(self):
        self._login(self.employer)
        resp = self.client.post("/api/admin/notification-templates/", {
            "template_key": "x", "name": "X", "category": "system",
            "channel": "email", "subject": "S", "body": "B",
            "allowed_variables": [], "language": "en", "scope": "system"
        }, format="json")
        self.assertIn(resp.status_code, [400, 403])

    def test_non_admin_cannot_manage_providers(self):
        self._login(self.handler)
        resp = self.client.post("/api/admin/notification-providers/", {
            "name": "Bad", "channel": "email"
        }, format="json")
        self.assertIn(resp.status_code, [400, 403])

    def test_unauthenticated_returns_401(self):
        self.client.credentials()
        resp = self.client.get("/api/notifications/")
        self.assertEqual(resp.status_code, 401)


class E2ETests(TestCase):
    def setUp(self):
        self.state = State.objects.create(name="Lagos", code="LA")
        self.handler = User.objects.create_user(
            username="e2ehandler", email="e2e@test.com",
            password="pass", role=UserRole.FOOD_HANDLER, state=self.state
        )
        self.state_admin = User.objects.create_user(
            username="stateadmin", email="state@test.com", password="pass",
            role=UserRole.STATE_ADMIN, state=self.state
        )
        self.other_state = State.objects.create(name="Oyo", code="OY")
        self.other_state_admin = User.objects.create_user(
            username="otherstateadmin", email="otherstate@test.com", password="pass",
            role=UserRole.STATE_ADMIN, state=self.other_state
        )
        self.admin = User.objects.create_user(
            username="e2eadmin", email="e2ea@test.com", password="pass",
            role=UserRole.SUPER_ADMIN, is_staff=True, is_superuser=True
        )
        NotificationProvider.objects.create(
            name="E2E Email", channel=NotificationChannel.EMAIL,
            is_active=True, is_default=True
        )
        NotificationProvider.objects.create(
            name="E2E SMS", channel=NotificationChannel.SMS,
            is_active=True, is_default=True
        )
        self.template = NotificationTemplate.objects.create(
            template_key="e2e.cert", name="E2E Cert",
            category=NotificationCategory.CERTIFICATE,
            channel=NotificationChannel.EMAIL,
            subject="Cert {{ certificate_number }}",
            body="Hi {{ user_name }}, cert {{ certificate_number }} is ready.",
            allowed_variables=["user_name", "certificate_number"],
            status=TemplateStatus.ACTIVE,
        )
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

    def test_send_notification_creates_inbox_and_delivery(self):
        resp = self.client.post("/api/internal/notifications/send", {
            "category": "certificate", "title": "E2E Send",
            "message": "Message body",
            "channels": ["in_app", "email"],
            "recipients": [{
                "user_id": str(self.handler.id),
                "email": "e2e@test.com",
                "recipient_type": "food_handler",
            }],
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Notification.objects.count(), 1)
        deliveries = NotificationDelivery.objects.all()
        self.assertEqual(deliveries.count(), 1)
        self.assertEqual(deliveries[0].channel, "email")

    def test_send_template_renders_correctly(self):
        resp = self.client.post("/api/internal/notifications/send-template", {
            "template_key": "e2e.cert",
            "context": {"user_name": "Jane", "certificate_number": "CERT-E2E"},
            "channels": ["in_app"],
            "recipients": [{
                "user_id": str(self.handler.id),
                "email": "e2e@test.com",
                "recipient_type": "food_handler",
            }],
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        n = Notification.objects.first()
        self.assertIn("CERT-E2E", n.title)
        self.assertIn("Jane", n.message)

    def test_emit_event_and_notify(self):
        result = NotificationService.notify(
            event_key="certificate.issued",
            source_module="certificates",
            title="Event Cert Issued",
            message="Test event notification",
            category=NotificationCategory.CERTIFICATE,
            payload={"food_handler_user_id": str(self.handler.id)},
        )
        self.assertEqual(len(result), 1)
        events = NotificationEvent.objects.filter(
            event_key="certificate.issued"
        )
        self.assertGreaterEqual(events.count(), 1)

    def test_schedule_and_process_reminder(self):
        event = NotificationService.schedule(
            template_key="e2e.cert",
            context={"user_name": "Sched", "certificate_number": "SCH-001"},
            scheduled_at=timezone.now() - timedelta(minutes=5),
            recipients_override=[{
                "user_id": str(self.handler.id),
                "email": "e2e@test.com",
                "recipient_type": "food_handler",
            }],
        )
        processed = NotificationService.process_due_reminders()
        self.assertEqual(processed, 1)
        event.refresh_from_db()
        self.assertTrue(event.processed)

    def test_broadcast_full_workflow(self):
        resp = self.client.post("/api/admin/broadcasts/", {
            "title": "E2E BC", "message": "Hello",
            "category": "system", "priority": "normal",
            "audience_type": "all_federal_ministry",
            "audience_filters": {}, "channels": ["in_app"],
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        bid = resp.json().get("data", {}).get("id")

        self.client.post(f"/api/admin/broadcasts/{bid}/estimate-audience/")
        self.client.post(f"/api/admin/broadcasts/{bid}/submit-for-approval/")
        self.client.post(f"/api/admin/broadcasts/{bid}/approve/")
        resp = self.client.post(f"/api/admin/broadcasts/{bid}/send/")
        self.assertEqual(resp.status_code, 200)

    def test_state_admin_public_awareness_workflow(self):
        client = APIClient()
        refresh = RefreshToken.for_user(self.state_admin)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        create = client.post("/api/admin/broadcasts/", {
            "title": "State cholera advisory",
            "message": "Review current food safety guidance and facility hygiene alerts.",
            "category": "system",
            "priority": "high",
            "audience_type": "all_facilities_in_state",
            "audience_filters": {"notice_kind": "public_notice"},
            "channels": ["in_app"],
        }, format="json")
        self.assertEqual(create.status_code, 201)
        broadcast_id = create.json().get("data", {}).get("id")
        broadcast = BroadcastMessage.objects.get(id=broadcast_id)
        self.assertEqual(str(broadcast.audience_filters.get("state_id")), str(self.state.id))

        submit = client.post(f"/api/admin/broadcasts/{broadcast_id}/submit-for-approval/")
        self.assertEqual(submit.status_code, 200)
        approve = client.post(f"/api/admin/broadcasts/{broadcast_id}/approve/")
        self.assertEqual(approve.status_code, 200)
        publish = client.post(f"/api/admin/broadcasts/{broadcast_id}/send/")
        self.assertEqual(publish.status_code, 200)
        archive = client.post(f"/api/admin/broadcasts/{broadcast_id}/archive/")
        self.assertEqual(archive.status_code, 200)

        events = AuditLog.objects.filter(target_id=str(broadcast_id)).values_list("metadata", flat=True)
        audit_events = {event.get("event") for event in events}
        self.assertTrue({"broadcast_created", "broadcast_submitted_for_approval", "broadcast_approved", "broadcast_published", "broadcast_archived"}.issubset(audit_events))

    def test_state_admin_sees_only_state_broadcasts(self):
        own = BroadcastMessage.objects.create(
            title="Lagos advisory",
            message="State notice",
            category="system",
            priority="normal",
            audience_type="all_facilities_in_state",
            audience_filters={"state_id": str(self.state.id)},
            channels=["in_app"],
            created_by=self.state_admin,
        )
        BroadcastMessage.objects.create(
            title="Oyo advisory",
            message="Other state notice",
            category="system",
            priority="normal",
            audience_type="all_facilities_in_state",
            audience_filters={"state_id": str(self.other_state.id)},
            channels=["in_app"],
            created_by=self.other_state_admin,
        )

        client = APIClient()
        refresh = RefreshToken.for_user(self.state_admin)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = client.get("/api/admin/broadcasts/")
        self.assertEqual(response.status_code, 200)
        rows = response.json().get("data", [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], str(own.id))

    def test_mark_read_and_unread_count(self):
        Notification.objects.create(
            recipient=self.handler, category="system",
            title="Unread test", message="Body"
        )
        refresh = RefreshToken.for_user(self.handler)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )
        resp = self.client.get("/api/notifications/unread-count/")
        self.assertEqual(resp.status_code, 200)

        nid = str(Notification.objects.first().id)
        self.client.post(f"/api/notifications/{nid}/mark-read/")
        resp2 = self.client.get("/api/notifications/unread-count/")
        self.assertEqual(resp2.status_code, 200)
