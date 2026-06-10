from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.forms.views import FormAssignmentViewSet, FormResponseViewSet, FormTemplateViewSet

router = DefaultRouter()
router.register("forms/templates", FormTemplateViewSet, basename="form-templates")
router.register("forms/assignments", FormAssignmentViewSet, basename="form-assignments")
router.register("forms/responses", FormResponseViewSet, basename="form-responses")

urlpatterns = router.urls
