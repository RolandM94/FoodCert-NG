from rest_framework.routers import DefaultRouter

from apps.facilities.views import FacilityAccreditationApplicationViewSet, MedicalFacilityViewSet

router = DefaultRouter()
router.register("medical-facilities", MedicalFacilityViewSet, basename="medical-facilities")
router.register("facility-accreditation", FacilityAccreditationApplicationViewSet, basename="facility-accreditation")

urlpatterns = router.urls
