from rest_framework.routers import DefaultRouter

from apps.lab_tests.views import LabTestViewSet


router = DefaultRouter()
router.register("lab-tests", LabTestViewSet, basename="lab-tests")

urlpatterns = router.urls
