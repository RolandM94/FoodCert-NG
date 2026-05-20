from rest_framework.routers import DefaultRouter

from apps.nin_verification.views import NINVerificationViewSet

router = DefaultRouter()
router.register("nin-verifications", NINVerificationViewSet, basename="nin-verifications")

urlpatterns = router.urls
