from rest_framework import serializers

from apps.nin_verification.models import NINVerification


class NINVerificationSerializer(serializers.ModelSerializer):
    masked_nin = serializers.CharField(read_only=True)
    food_handler_name = serializers.CharField(source="food_handler.full_name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)

    class Meta:
        model = NINVerification
        fields = (
            "id",
            "food_handler",
            "food_handler_name",
            "masked_nin",
            "provider",
            "provider_reference",
            "status",
            "verified_full_name",
            "verified_date_of_birth",
            "verified_gender",
            "verified_photo_url",
            "match_score",
            "mismatch_fields",
            "verified_at",
            "reviewed_by",
            "reviewed_by_name",
            "review_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class NINOverrideSerializer(serializers.Serializer):
    review_notes = serializers.CharField(required=False, allow_blank=True)
