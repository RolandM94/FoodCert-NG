from rest_framework.routers import DefaultRouter

from apps.assessments.views import AppointmentViewSet, HealthDeclarationViewSet, MedicalAssessmentViewSet


router = DefaultRouter()
router.register("appointments", AppointmentViewSet, basename="appointments")
router.register("assessments", MedicalAssessmentViewSet, basename="assessments")
router.register("declarations", HealthDeclarationViewSet, basename="declarations")

urlpatterns = router.urls
