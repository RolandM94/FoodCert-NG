from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.assessments.views import AssessmentFormAnalyticsView, AssessmentFormQuestionViewSet, AssessmentFormResponseViewSet, AssessmentFormSectionViewSet, AssessmentFormTemplateViewSet, AssessmentRequirementResolveView, AssessmentRequirementSetViewSet, AppointmentViewSet, DoctorAssessmentViewSet, HealthDeclarationViewSet, MedicalAssessmentViewSet


router = DefaultRouter()
router.register("appointments", AppointmentViewSet, basename="appointments")
router.register("assessments", MedicalAssessmentViewSet, basename="assessments")
router.register("declarations", HealthDeclarationViewSet, basename="declarations")
router.register("doctor/assessments", DoctorAssessmentViewSet, basename="doctor-assessments")
router.register("assessment-forms/templates", AssessmentFormTemplateViewSet, basename="assessment-form-templates")
router.register("assessment-forms/sections", AssessmentFormSectionViewSet, basename="assessment-form-sections")
router.register("assessment-forms/questions", AssessmentFormQuestionViewSet, basename="assessment-form-questions")
router.register("assessment-forms/requirement-sets", AssessmentRequirementSetViewSet, basename="assessment-requirement-sets")
router.register("assessment-form-responses", AssessmentFormResponseViewSet, basename="assessment-form-responses")

urlpatterns = [
    path("assessment-forms/analytics/", AssessmentFormAnalyticsView.as_view(), name="assessment-forms-analytics"),
    path("assessment-forms/requirements/resolve/", AssessmentRequirementResolveView.as_view(), name="assessment-requirements-resolve"),
] + router.urls
