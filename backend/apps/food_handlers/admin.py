from django.contrib import admin

from apps.food_handlers.models import FoodHandlerProfile


@admin.register(FoodHandlerProfile)
class FoodHandlerProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "system_identifier", "food_handler_category", "current_status", "state", "employer")
    list_filter = ("food_handler_category", "current_status", "state")
    search_fields = ("full_name", "system_identifier", "email", "phone")
    exclude = ("nin",)
