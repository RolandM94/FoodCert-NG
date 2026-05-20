from rest_framework.routers import DefaultRouter

from apps.employers.views import EmployerViewSet

router = DefaultRouter()
router.register("employers", EmployerViewSet, basename="employers")

urlpatterns = router.urls
