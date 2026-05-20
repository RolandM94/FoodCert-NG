from django.contrib import admin

from apps.certificates.models import Certificate, CertificateRequest, CertificateVerificationLog


@admin.register(CertificateRequest)
class CertificateRequestAdmin(admin.ModelAdmin):
    list_display = ("assessment", "status", "requested_by", "reviewed_by", "reviewed_at", "created_at")
    list_filter = ("status", "reviewed_at", "created_at")
    search_fields = ("assessment__food_handler__full_name", "assessment__facility__facility_name")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("certificate_number", "food_handler", "facility", "issuing_state", "status", "issue_date", "expiry_date")
    list_filter = ("status", "issuing_state", "issue_date", "expiry_date")
    search_fields = ("certificate_number", "food_handler__full_name", "facility__facility_name")
    readonly_fields = (
        "certificate_number",
        "food_handler",
        "assessment",
        "employer",
        "facility",
        "doctor",
        "issuing_state",
        "issued_by_state_user",
        "issue_date",
        "expiry_date",
        "qr_code_url",
        "verification_url",
        "pdf_url",
        "digital_signature_hash",
    )


@admin.register(CertificateVerificationLog)
class CertificateVerificationLogAdmin(admin.ModelAdmin):
    list_display = ("certificate_number_submitted", "result", "ip_address", "verified_at")
    list_filter = ("result", "verified_at")
    search_fields = ("certificate_number_submitted",)
