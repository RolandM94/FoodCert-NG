from rest_framework.routers import DefaultRouter

from apps.facilities.views import FacilityAccreditationApplicationViewSet, FacilityDocumentViewSet, MedicalFacilityViewSet

router = DefaultRouter()
router.register("medical-facilities", MedicalFacilityViewSet, basename="medical-facilities")
router.register("facilities", MedicalFacilityViewSet, basename="facilities")
router.register("facility-accreditation", FacilityAccreditationApplicationViewSet, basename="facility-accreditation")
router.register("facility-documents", FacilityDocumentViewSet, basename="facility-documents")

urlpatterns = router.urls
