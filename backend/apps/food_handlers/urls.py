from rest_framework.routers import DefaultRouter

from apps.food_handlers.views import FoodHandlerProfileViewSet

router = DefaultRouter()
router.register("food-handlers", FoodHandlerProfileViewSet, basename="food-handlers")

urlpatterns = router.urls
