from django.contrib import admin

from ...admin_site import edc_pharmacy_admin
from ...forms import LocationForm
from ...models import Location
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Location, site=edc_pharmacy_admin)
class LocationAdmin(ModelAdminMixin, admin.ModelAdmin):
    ordering = ("name",)

    form = LocationForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "display_name",
                    "site",
                )
            },
        ),
    )

    search_fields = ["id", "name"]
