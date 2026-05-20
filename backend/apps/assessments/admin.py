from django.contrib import admin

from apps.assessments.models import Appointment, HealthDeclaration, MedicalAssessment, PhysicalExamination


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
    list_display = ("assessment", "risk_flag", "submitted_at", "validated_by_doctor", "validated_at")
    list_filter = ("risk_flag", "submitted_at", "validated_at")
    search_fields = ("assessment__food_handler__full_name",)


@admin.register(PhysicalExamination)
class PhysicalExaminationAdmin(admin.ModelAdmin):
    list_display = ("assessment", "examined_by", "examined_at")
    list_filter = ("examined_at",)
    search_fields = ("assessment__food_handler__full_name", "examined_by__email")
