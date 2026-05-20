from django.contrib import admin

from apps.locations.models import LGA, State, Ward


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_fct")
    search_fields = ("name", "code")


@admin.register(LGA)
class LGAAdmin(admin.ModelAdmin):
    list_display = ("name", "state")
    list_filter = ("state",)
    search_fields = ("name", "state__name")


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ("name", "lga")
    list_filter = ("lga__state",)
    search_fields = ("name", "lga__name")
