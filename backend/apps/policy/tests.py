from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.audit.models import AuditAction, AuditLog
from apps.locations.models import State
from apps.organizations.models import Organization, OrganizationType
from apps.policy.models import StatePolicyConfig


User = get_user_model()


def payload(response):
    if isinstance(response.data, dict):
        return response.data.get("data", response.data)
    return response.data


class StateMedicalFacilitySettingsTests(APITestCase):
    def setUp(self):
        self.lagos = State.objects.create(name="Lagos", code="LA")
        self.state_admin = User.objects.create_user(
            "lagos-admin",
            "lagos-admin@example.com",
            "StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=self.lagos,
        )
        self.employer = User.objects.create_user(
            "employer-user",
            "employer@example.com",
            "StrongPass123!",
            role=UserRole.EMPLOYER,
            state=self.lagos,
        )

    def test_state_admin_get_creates_default_medical_facility_settings(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state-policy-configs/my-medical-facility-settings/")

        self.assertEqual(response.status_code, 200)
        data = payload(response)
        self.assertEqual(str(data["state"]), str(self.lagos.id))
        self.assertEqual(data["medical_facility_settings"]["validity_duration"], 12)
        self.assertEqual(data["medical_facility_settings"]["reminder_days_before_expiry"], [60, 30, 7])
        self.assertTrue(StatePolicyConfig.objects.filter(state=self.lagos).exists())

    def test_state_admin_can_update_medical_facility_settings(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.patch(
            "/api/state-policy-configs/my-medical-facility-settings/",
            {
                "medical_facility_settings": {
                    "accreditation_template": "template-accreditation",
                    "reaccreditation_template": "template-renewal",
                    "validity_duration": 2,
                    "validity_unit": "years",
                    "initial_review_sla": 10,
                    "review_day_type": "working_days",
                    "correction_window": 5,
                    "correction_day_type": "calendar_days",
                    "renewal_window_days": 45,
                    "grace_period_days": 7,
                    "reminder_days_before_expiry": [45, 14],
                    "escalation_days_after_sla": [2, 5],
                    "disable_assessments_when_expired": True,
                    "disable_assessments_when_suspended": True,
                    "allow_renewal_after_expiry": True,
                    "allow_suspended_renewal": False,
                    "auto_expire_on_expiry_date": True,
                    "require_state_approval_to_reactivate": True,
                    "require_reinspection_before_reactivation": True,
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = payload(response)
        self.assertEqual(data["medical_facility_settings"]["validity_unit"], "years")
        self.assertEqual(data["medical_facility_settings"]["reminder_days_before_expiry"], [45, 14])
        self.assertEqual(str(data["updated_by"]), str(self.state_admin.id))

    def test_non_state_admin_cannot_manage_medical_facility_settings(self):
        self.client.force_authenticate(self.employer)

        response = self.client.get("/api/state-policy-configs/my-medical-facility-settings/")

        self.assertEqual(response.status_code, 403)

    def test_invalid_medical_facility_settings_are_rejected(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.patch(
            "/api/state-policy-configs/my-medical-facility-settings/",
            {"medical_facility_settings": {"validity_duration": 0}},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_state_admin_can_update_core_account_settings(self):
        self.client.force_authenticate(self.state_admin)

        profile_response = self.client.patch(
            "/api/state-policy-configs/my-state-profile/",
            {"state_profile_settings": {"ministry_name": "Lagos State Ministry of Health", "public_display_name": "Lagos State MOH"}},
            format="json",
        )
        notification_response = self.client.patch(
            "/api/state-policy-configs/my-notification-settings/",
            {"notification_settings": {"channels": {"in_app": True, "email": True, "sms": False, "whatsapp": False}}},
            format="json",
        )
        security_response = self.client.patch(
            "/api/state-policy-configs/my-security-access-settings/",
            {"security_access_settings": {"minimum_password_length": 12, "session_timeout_minutes": 360, "idle_timeout_minutes": 20, "failed_login_attempts": 4}},
            format="json",
        )

        self.assertEqual(profile_response.status_code, 200)
        self.assertEqual(notification_response.status_code, 200)
        self.assertEqual(security_response.status_code, 200)
        self.assertEqual(payload(profile_response)["state_profile_settings"]["public_display_name"], "Lagos State MOH")
        self.assertTrue(payload(notification_response)["notification_settings"]["event_rules"]["security"])
        self.assertEqual(payload(security_response)["security_access_settings"]["minimum_password_length"], 12)
        self.assertEqual(AuditLog.objects.filter(metadata__module="Account Settings").count(), 3)

    def test_invalid_security_settings_are_rejected(self):
        self.client.force_authenticate(self.state_admin)

        response = self.client.patch(
            "/api/state-policy-configs/my-security-access-settings/",
            {"security_access_settings": {"minimum_password_length": 0}},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_state_audit_logs_are_state_scoped(self):
        other_state = State.objects.create(name="Oyo", code="OY")
        AuditLog.objects.create(actor=self.state_admin, action=AuditAction.UPDATE, state=self.lagos, metadata={"event": "lagos_event", "module": "Account Settings"})
        AuditLog.objects.create(actor=self.state_admin, action=AuditAction.UPDATE, state=other_state, metadata={"event": "oyo_event", "module": "Account Settings"})
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state-policy-configs/my-audit-logs/")

        self.assertEqual(response.status_code, 200)
        events = [item["event"] for item in payload(response)]
        self.assertIn("lagos_event", events)
        self.assertNotIn("oyo_event", events)

    def test_state_audit_logs_prefer_current_organization_scope(self):
        lagos_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=self.lagos)
        other_lagos_org = Organization.objects.create(name="Other Lagos Regulator", organization_type=OrganizationType.STATE_MINISTRY, state=self.lagos)
        self.state_admin.organization = lagos_org
        self.state_admin.save(update_fields=["organization"])
        AuditLog.objects.create(actor=self.state_admin, action=AuditAction.UPDATE, organization=lagos_org, state=self.lagos, metadata={"event": "own_org_event", "module": "Account Settings"})
        AuditLog.objects.create(actor=self.state_admin, action=AuditAction.UPDATE, organization=other_lagos_org, state=self.lagos, metadata={"event": "other_org_event", "module": "Account Settings"})
        AuditLog.objects.create(actor=self.state_admin, action=AuditAction.UPDATE, state=self.lagos, metadata={"event": "legacy_state_event", "module": "Account Settings"})
        self.client.force_authenticate(self.state_admin)

        response = self.client.get("/api/state-policy-configs/my-audit-logs/")

        self.assertEqual(response.status_code, 200)
        events = [item["event"] for item in payload(response)]
        self.assertIn("own_org_event", events)
        self.assertIn("legacy_state_event", events)
        self.assertNotIn("other_org_event", events)

    def test_state_audit_logs_support_extended_filters_and_scope_fields(self):
        inspector = User.objects.create_user(
            "lagos-inspector",
            "inspector@example.com",
            "StrongPass123!",
            role=UserRole.INSPECTOR,
            state=self.lagos,
            first_name="Ife",
            last_name="Inspector",
        )
        log = AuditLog.objects.create(
            actor=inspector,
            action=AuditAction.WORKFLOW_TRANSITION,
            state=self.lagos,
            metadata={
                "event": "public_notice_published",
                "entity": "BroadcastMessage",
                "facility_id": "facility-123",
                "facility_name": "Mainland Diagnostics",
                "lga_id": "lga-ikeja",
                "lga_name": "Ikeja",
            },
            target_type="BroadcastMessage",
            target_id="broadcast-123",
        )
        self.client.force_authenticate(self.state_admin)

        response = self.client.get(
            "/api/state-policy-configs/my-audit-logs/",
            {
                "actor": "Ife",
                "role": UserRole.INSPECTOR,
                "action": AuditAction.WORKFLOW_TRANSITION,
                "entity": "BroadcastMessage",
                "date_from": timezone.localdate().isoformat(),
                "date_to": timezone.localdate().isoformat(),
                "lga": "Ikeja",
                "facility": "Mainland",
            },
        )

        self.assertEqual(response.status_code, 200)
        rows = payload(response)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], str(log.id))
        self.assertEqual(rows[0]["actor_role"], "Inspector")
        self.assertEqual(rows[0]["module"], "Public Awareness")
        self.assertEqual(rows[0]["event"], "Public notice published")
        self.assertEqual(rows[0]["entity"], "BroadcastMessage")
        self.assertEqual(rows[0]["entity_label"], "BroadcastMessage")
        self.assertEqual(rows[0]["lga_name"], "Ikeja")
        self.assertEqual(rows[0]["facility_name"], "Mainland Diagnostics")
        self.assertEqual(rows[0]["risk_level"], "medium")
