from rest_framework.routers import DefaultRouter

from apps.policy.views import StatePolicyConfigViewSet

router = DefaultRouter()
router.register("state-policy-configs", StatePolicyConfigViewSet, basename="state-policy-configs")

urlpatterns = router.urls
