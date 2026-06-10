from rest_framework import serializers

from apps.forms.models import (
    FormAssignment, FormResponse, FormTemplate, FormTemplateVersion,
)


class FormTemplateSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner_organization.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    response_count = serializers.SerializerMethodField()

    class Meta:
        model = FormTemplate
        fields = (
            "id", "title", "description", "purpose", "owner_organization", "owner_name",
            "target_respondent_type", "module_context", "status", "current_version",
            "created_by", "created_by_name", "response_count", "created_at", "updated_at",
        )
        read_only_fields = ("id", "owner_name", "created_by_name", "response_count", "created_at", "updated_at")

    def get_response_count(self, obj):
        return obj.responses.count()


class FormTemplateVersionSerializer(serializers.ModelSerializer):
    published_by_name = serializers.CharField(source="published_by.get_full_name", read_only=True)

    class Meta:
        model = FormTemplateVersion
        fields = (
            "id", "template", "version_number", "schema_json", "scoring_json",
            "conditional_logic_json", "published_by", "published_by_name",
            "published_at", "status", "created_at",
        )
        read_only_fields = ("id", "published_by_name", "created_at")


class FormAssignmentSerializer(serializers.ModelSerializer):
    template_title = serializers.CharField(source="template.title", read_only=True)
    assigned_by_name = serializers.CharField(source="assigned_by.get_full_name", read_only=True)
    response_count = serializers.SerializerMethodField()

    class Meta:
        model = FormAssignment
        fields = (
            "id", "title", "template", "template_title", "template_version",
            "purpose", "assigned_by", "assigned_by_name",
            "assigned_to_type", "assigned_to_id", "recipient_role",
            "context_type", "context_id",
            "start_date", "due_date",
            "allow_draft", "allow_multiple_submissions", "allow_late_submission",
            "requires_review", "reviewer_role",
            "status", "response_count", "created_at", "updated_at",
        )
        read_only_fields = ("id", "assigned_by_name", "template_title", "response_count", "created_at", "updated_at")

    def get_response_count(self, obj):
        return obj.responses.count()


class FormResponseSerializer(serializers.ModelSerializer):
    template_title = serializers.CharField(source="template.title", read_only=True)
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    respondent_name = serializers.CharField(source="respondent_user.get_full_name", read_only=True)
    respondent_email = serializers.EmailField(source="respondent_user.email", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)

    class Meta:
        model = FormResponse
        fields = (
            "id", "assignment", "assignment_title", "template", "template_title",
            "template_version", "respondent_user", "respondent_name", "respondent_email",
            "respondent_organization", "context_type", "context_id",
            "response_json", "score", "risk_rating",
            "status", "submitted_at",
            "reviewed_by", "reviewed_by_name", "reviewed_at",
            "review_notes", "returned_reason",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "template_title", "assignment_title", "respondent_name",
                            "respondent_email", "reviewed_by_name", "created_at", "updated_at")
