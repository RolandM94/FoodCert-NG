from rest_framework.routers import DefaultRouter

from apps.locations.views import LGAViewSet, StateViewSet, WardViewSet


router = DefaultRouter()
router.register("states", StateViewSet, basename="states")
router.register("lgas", LGAViewSet, basename="lgas")
router.register("wards", WardViewSet, basename="wards")

urlpatterns = router.urls
