from django.contrib import admin

from apps.assessments.models import AssessmentFormQuestion, AssessmentFormResponse, AssessmentFormSection, AssessmentFormTemplate, AssessmentRequirementSet, Appointment, HealthDeclaration, MedicalAssessment, PhysicalExamination


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("food_handler", "facility", "appointment_date", "status")
    list_filter = ("status", "facility", "appointment_date")
    search_fields = ("food_handler__full_name", "facility__facility_name")


@admin.register(MedicalAssessment)
class MedicalAssessmentAdmin(admin.ModelAdmin):
    list_display = ("food_handler", "facility", "doctor", "status", "final_decision", "signed_at")
    list_filter = ("status", "final_decision", "facility", "created_at")
    search_fields = ("food_handler__full_name", "facility__facility_name", "doctor__email")


@admin.register(HealthDeclaration)
class HealthDeclarationAdmin(admin.ModelAdmin):
    list_display = ("assessment", "version", "risk_flag", "is_locked", "submitted_at", "validated_by_doctor", "validated_at")
    list_filter = ("risk_flag", "is_locked", "submitted_at", "validated_at")
    search_fields = ("assessment__food_handler__full_name",)


@admin.register(PhysicalExamination)
class PhysicalExaminationAdmin(admin.ModelAdmin):
    list_display = ("assessment", "examined_by", "risk_flag", "is_completed", "completed_at", "examined_at")
    list_filter = ("risk_flag", "is_completed", "examined_at")
    search_fields = ("assessment__food_handler__full_name", "examined_by__email")


@admin.register(AssessmentFormTemplate)
class AssessmentFormTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "form_type", "scope", "version", "status", "is_mandatory", "reviewed_by", "reviewed_at")
    list_filter = ("scope", "form_type", "status", "is_mandatory")
    search_fields = ("name", "description")


@admin.register(AssessmentFormSection)
class AssessmentFormSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "template", "key", "sort_order", "required_completion")
    list_filter = ("required_completion",)
    search_fields = ("title", "key", "template__name")


@admin.register(AssessmentFormQuestion)
class AssessmentFormQuestionAdmin(admin.ModelAdmin):
    list_display = ("label", "section", "key", "question_type", "privacy_classification", "respondent_role", "required")
    list_filter = ("question_type", "privacy_classification", "respondent_role", "required", "is_active")
    search_fields = ("label", "key", "section__template__name")


@admin.register(AssessmentRequirementSet)
class AssessmentRequirementSetAdmin(admin.ModelAdmin):
    list_display = ("name", "scope", "assessment_type", "version", "status", "effective_from", "effective_to")
    list_filter = ("scope", "assessment_type", "status")
    search_fields = ("name", "description")


@admin.register(AssessmentFormResponse)
class AssessmentFormResponseAdmin(admin.ModelAdmin):
    list_display = ("assessment", "template", "template_version", "respondent_role", "status", "version", "is_locked")
    list_filter = ("respondent_role", "status", "is_required", "is_locked")
    search_fields = ("assessment__food_handler__full_name", "template__name", "respondent__email")
