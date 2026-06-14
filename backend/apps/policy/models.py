from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


def default_medical_facility_settings():
    return {
        "accreditation_template": "",
        "reaccreditation_template": "",
        "validity_duration": 12,
        "validity_unit": "months",
        "initial_review_sla": 14,
        "review_day_type": "working_days",
        "correction_window": 7,
        "correction_day_type": "calendar_days",
        "renewal_window_days": 60,
        "grace_period_days": 0,
        "reminder_days_before_expiry": [60, 30, 7],
        "escalation_days_after_sla": [3, 7],
        "disable_assessments_when_expired": True,
        "disable_assessments_when_suspended": True,
        "allow_renewal_after_expiry": True,
        "allow_suspended_renewal": False,
        "auto_expire_on_expiry_date": True,
        "require_state_approval_to_reactivate": True,
        "require_reinspection_before_reactivation": False,
    }


def default_state_profile_settings():
    return {
        "ministry_name": "",
        "public_display_name": "",
        "official_email": "",
        "official_phone": "",
        "website": "",
        "address_line_1": "",
        "address_line_2": "",
        "city": "",
        "country": "Nigeria",
        "postal_code": "",
        "state_logo_url": "",
        "state_seal_url": "",
        "certificate_logo_url": "",
        "receipt_logo_url": "",
        "primary_brand_color": "#16A34A",
        "secondary_brand_color": "#0F766E",
        "signatories": [],
        "timezone": "Africa/Lagos",
        "currency": "NGN",
        "working_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
        "working_hours_start": "09:00",
        "working_hours_end": "17:00",
        "public_holidays_source": "federal_and_state",
    }


def default_notification_settings():
    return {
        "channels": {
            "in_app": True,
            "email": True,
            "sms": False,
            "whatsapp": False,
            "sender_name": "FoodCert NG",
            "reply_to_email": "",
        },
        "event_rules": {
            "facility_accreditation": True,
            "certificate_validation": True,
            "inspection_enforcement": True,
            "forms": True,
            "payments": True,
            "security": True,
        },
        "reminder_schedules": {
            "certificate_expiry": [30, 14, 7],
            "facility_accreditation_expiry": [90, 60, 30, 14, 7],
            "inspection_due": [7, 3, 1],
            "corrective_action_due": [3, 1, 0],
            "form_due": [7, 3, 1],
        },
        "recipient_roles": {
            "state_admin": True,
            "assigned_reviewer": True,
            "assigned_inspector": True,
            "facility_admin": True,
            "employer_admin": True,
        },
        "templates_enabled": True,
        "delivery_logs_visible": True,
    }


def default_security_access_settings():
    return {
        "minimum_password_length": 10,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_number": True,
        "require_symbol": False,
        "password_expiry_days": 0,
        "prevent_password_reuse": 5,
        "force_password_reset_for_new_users": True,
        "mfa_required_for_admins": True,
        "mfa_required_for_finance": False,
        "mfa_required_for_certificate_approvers": True,
        "allowed_mfa_methods": ["authenticator_app", "email_otp"],
        "session_timeout_minutes": 480,
        "idle_timeout_minutes": 30,
        "concurrent_sessions_allowed": 2,
        "force_logout_on_role_change": True,
        "failed_login_attempts": 5,
        "lockout_duration_minutes": 30,
        "notify_admin_on_lockout": True,
        "allowed_email_domains": [],
        "block_public_email_domains": False,
        "enable_api_access": False,
        "allow_api_tokens": False,
        "require_token_expiry": True,
        "require_sensitive_export_approval": True,
        "restrict_medical_data_export": True,
        "watermark_pdf_exports": True,
        "audit_all_exports": True,
        "enable_periodic_access_review": True,
        "access_review_frequency_days": 90,
    }


class NationalPolicyConfig(BaseModel):
    certificate_validity_months = models.PositiveIntegerField(default=settings.DEFAULT_CERTIFICATE_VALIDITY_MONTHS)
    renewal_reminder_days = models.JSONField(default=list)
    typhoid_validity_years = models.PositiveIntegerField(default=settings.DEFAULT_TYPHOID_VALIDITY_YEARS)
    hepatitis_a_second_dose_months = models.PositiveIntegerField(default=settings.DEFAULT_HEPATITIS_A_SECOND_DOSE_MONTHS)
    nin_required = models.BooleanField(default=True)
    payment_before_assessment_required = models.BooleanField(default=True)
    state_validation_before_certificate_required = models.BooleanField(default=True)
    public_qr_verification_enabled = models.BooleanField(default=True)
    state_certificate_template_overrides_enabled = models.BooleanField(default=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_national_policy_configs",
    )

    def save(self, *args, **kwargs):
        if not self.renewal_reminder_days:
            self.renewal_reminder_days = [30, 7]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return "National policy configuration"


class StatePolicyConfig(BaseModel):
    state = models.OneToOneField("locations.State", on_delete=models.CASCADE, related_name="policy_config")
    requires_state_certificate_validation = models.BooleanField(default=True)
    certificate_validity_months = models.PositiveIntegerField(default=settings.DEFAULT_CERTIFICATE_VALIDITY_MONTHS)
    typhoid_validity_years = models.PositiveIntegerField(default=settings.DEFAULT_TYPHOID_VALIDITY_YEARS)
    hepatitis_a_second_dose_months = models.PositiveIntegerField(default=settings.DEFAULT_HEPATITIS_A_SECOND_DOSE_MONTHS)
    auto_renewal_reminder_days = models.JSONField(default=list)
    medical_facility_settings = models.JSONField(default=default_medical_facility_settings, blank=True)
    state_profile_settings = models.JSONField(default=default_state_profile_settings, blank=True)
    notification_settings = models.JSONField(default=default_notification_settings, blank=True)
    security_access_settings = models.JSONField(default=default_security_access_settings, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_state_policy_configs",
    )

    class Meta:
        indexes = [models.Index(fields=["state"])]

    def save(self, *args, **kwargs):
        if not self.auto_renewal_reminder_days:
            self.auto_renewal_reminder_days = [30, 7]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.state.name} policy"
