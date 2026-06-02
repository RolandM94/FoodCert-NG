from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.assessments.views import AssessmentFormQuestionViewSet, AssessmentFormResponseViewSet, AssessmentFormSectionViewSet, AssessmentFormTemplateViewSet, AssessmentRequirementResolveView, AssessmentRequirementSetViewSet, AppointmentViewSet, DoctorAssessmentViewSet, HealthDeclarationViewSet, MedicalAssessmentViewSet


router = DefaultRouter()
router.register("appointments", AppointmentViewSet, basename="appointments")
router.register("assessments", MedicalAssessmentViewSet, basename="assessments")
router.register("declarations", HealthDeclarationViewSet, basename="declarations")
router.register("doctor/assessments", DoctorAssessmentViewSet, basename="doctor-assessments")
router.register("forms/templates", AssessmentFormTemplateViewSet, basename="assessment-form-templates")
router.register("forms/sections", AssessmentFormSectionViewSet, basename="assessment-form-sections")
router.register("forms/questions", AssessmentFormQuestionViewSet, basename="assessment-form-questions")
router.register("forms/requirement-sets", AssessmentRequirementSetViewSet, basename="assessment-requirement-sets")
router.register("form-responses", AssessmentFormResponseViewSet, basename="assessment-form-responses")

urlpatterns = [
    path("forms/requirements/resolve/", AssessmentRequirementResolveView.as_view(), name="assessment-requirements-resolve"),
] + router.urls
