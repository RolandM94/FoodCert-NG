from copy import deepcopy

from rest_framework import serializers


IDENTIFIER_KEYS = {
    "nin",
    "full_nin",
    "raw_nin",
    "national_identification_number",
    "bvn",
}

CLINICAL_KEYS = {
    "diagnosis",
    "doctor_note",
    "doctor_notes",
    "clinical_notes",
    "declaration_answer",
    "declaration_answers",
    "health_declaration",
    "lab_result",
    "lab_results",
    "result_notes",
    "doctor_review_notes",
    "lab_staff_notes",
    "medical_result",
    "medical_results",
    "treatment",
    "treatment_note",
    "treatment_notes",
    "decision_draft_notes",
}

FINANCE_SECRET_KEYS = {
    "bank_account",
    "bank_account_number",
    "bank_details",
    "account_number",
    "encrypted_secret_key",
    "webhook_secret",
    "secret_key",
    "payment_secret",
    "provider_secret",
}

PII_KEYS = {
    "full_name",
    "phone",
    "email",
    "home_address",
    "address",
    "passport_photo",
    "date_of_birth",
    "emergency_contact",
}

FINANCE_KEYS = {
    "amount",
    "gross_amount",
    "facility_amount",
    "state_amount",
    "platform_amount",
    "provider_reference",
    "internal_reference",
    "payment_provider",
    "payment_transaction",
    "settlement_status",
}


class PrivacySafeReportSerializer(serializers.Serializer):
    blocked_keys = IDENTIFIER_KEYS | CLINICAL_KEYS | FINANCE_SECRET_KEYS
    aggregate_only = False

    def to_representation(self, instance):
        return self.sanitize(deepcopy(instance))

    def sanitize(self, value):
        if isinstance(value, list):
            return [self.sanitize(item) for item in value]
        if isinstance(value, tuple):
            return [self.sanitize(item) for item in value]
        if isinstance(value, dict):
            cleaned = {}
            for key, item in value.items():
                normalized = self.normalize_key(key)
                if normalized in self.blocked_keys:
                    continue
                if self.aggregate_only and normalized in PII_KEYS:
                    continue
                cleaned[key] = self.sanitize(item)
            return cleaned
        return value

    @staticmethod
    def normalize_key(key):
        return str(key).strip().lower()


class FoodHandlerReportSerializer(PrivacySafeReportSerializer):
    blocked_keys = CLINICAL_KEYS | FINANCE_SECRET_KEYS | {"nin", "full_nin", "raw_nin"}


class EmployerSafeComplianceSerializer(PrivacySafeReportSerializer):
    blocked_keys = IDENTIFIER_KEYS | CLINICAL_KEYS | FINANCE_SECRET_KEYS


class InspectorSafeReportSerializer(PrivacySafeReportSerializer):
    blocked_keys = IDENTIFIER_KEYS | CLINICAL_KEYS | FINANCE_SECRET_KEYS | FINANCE_KEYS


class FacilityOperationalSerializer(PrivacySafeReportSerializer):
    blocked_keys = IDENTIFIER_KEYS | FINANCE_SECRET_KEYS


class StateRegulatoryReportSerializer(PrivacySafeReportSerializer):
    blocked_keys = IDENTIFIER_KEYS | CLINICAL_KEYS | FINANCE_SECRET_KEYS


class FederalAggregateReportSerializer(PrivacySafeReportSerializer):
    blocked_keys = IDENTIFIER_KEYS | CLINICAL_KEYS | FINANCE_SECRET_KEYS
    aggregate_only = True


class FinanceReportSerializer(PrivacySafeReportSerializer):
    blocked_keys = IDENTIFIER_KEYS | CLINICAL_KEYS | FINANCE_SECRET_KEYS


class MedicalRestrictedSerializer(PrivacySafeReportSerializer):
    blocked_keys = IDENTIFIER_KEYS | FINANCE_SECRET_KEYS


class AdminReportSerializer(PrivacySafeReportSerializer):
    blocked_keys = IDENTIFIER_KEYS | CLINICAL_KEYS | FINANCE_SECRET_KEYS | FINANCE_KEYS | PII_KEYS
