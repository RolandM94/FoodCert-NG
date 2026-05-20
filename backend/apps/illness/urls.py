from rest_framework.routers import DefaultRouter

from apps.illness.views import IllnessReportViewSet


router = DefaultRouter()
router.register("illness-reports", IllnessReportViewSet, basename="illness-reports")

urlpatterns = router.urls
