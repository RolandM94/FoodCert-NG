from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.vaccinations.views import VaccinationRecordViewSet


router = DefaultRouter()
router.register("vaccinations", VaccinationRecordViewSet, basename="vaccinations")

food_handler_vaccinations = VaccinationRecordViewSet.as_view({"get": "list"})

urlpatterns = [
    path("food-handlers/<uuid:food_handler_id>/vaccinations/", food_handler_vaccinations, name="food-handler-vaccinations"),
    *router.urls,
]
