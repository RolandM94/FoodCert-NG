from rest_framework.routers import DefaultRouter

from apps.inspections.views import InspectionViewSet


router = DefaultRouter()
router.register("inspections", InspectionViewSet, basename="inspections")

urlpatterns = router.urls
