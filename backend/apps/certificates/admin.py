from django.contrib import admin

from apps.certificates.models import Certificate, CertificateRequest, CertificateTemplate, CertificateVerificationLog, SuspiciousCertificateReport


@admin.register(CertificateRequest)
class CertificateRequestAdmin(admin.ModelAdmin):
    list_display = ("assessment", "status", "requested_by", "reviewed_by", "reviewed_at", "created_at")
    list_filter = ("status", "reviewed_at", "created_at")
    search_fields = ("assessment__food_handler__full_name", "assessment__facility__facility_name")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("certificate_number", "food_handler", "facility", "issuing_state", "template", "status", "issue_date", "expiry_date")
    list_filter = ("status", "issuing_state", "template", "issue_date", "expiry_date")
    search_fields = ("certificate_number", "food_handler__full_name", "facility__facility_name")
    readonly_fields = (
        "certificate_number",
        "public_id",
        "verification_token",
        "food_handler",
        "assessment",
        "employer",
        "business_branch",
        "facility",
        "doctor",
        "issuing_state",
        "issued_by_state_user",
        "template",
        "issue_date",
        "expiry_date",
        "qr_code_url",
        "verification_url",
        "pdf_url",
        "digital_signature_hash",
        "replaced_by",
        "replacement_reason",
        "suspended_by",
        "suspended_at",
        "suspension_reason",
    )


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "scope", "state", "is_active", "is_default", "updated_at")
    list_filter = ("scope", "state", "is_active", "is_default")
    search_fields = ("name", "ministry_name", "signatory_name")


@admin.register(CertificateVerificationLog)
class CertificateVerificationLogAdmin(admin.ModelAdmin):
    list_display = ("certificate_number_submitted", "verification_token_submitted", "result", "verifier_type", "ip_address", "verified_at")
    list_filter = ("result", "verifier_type", "verified_at")
    search_fields = ("certificate_number_submitted", "verification_token_submitted")


@admin.register(SuspiciousCertificateReport)
class SuspiciousCertificateReportAdmin(admin.ModelAdmin):
    list_display = ("certificate_number_submitted", "reason", "reporter_contact", "created_at")
    list_filter = ("created_at",)
    search_fields = ("certificate_number_submitted", "verification_token_submitted", "reason", "reporter_contact")
