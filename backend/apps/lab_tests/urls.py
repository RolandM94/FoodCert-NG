from rest_framework.routers import DefaultRouter

from apps.lab_tests.views import LabRequestViewSet, LabTestViewSet


router = DefaultRouter()
router.register("lab-tests", LabTestViewSet, basename="lab-tests")
router.register("lab/requests", LabRequestViewSet, basename="lab-requests")

urlpatterns = router.urls
