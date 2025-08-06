from django.contrib import admin
from edc_model_admin.history import SimpleHistoryAdmin

from ...admin_site import edc_pharmacy_admin
from ...forms import LocationForm
from ...models import Location
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Location, site=edc_pharmacy_admin)
class LocationAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    history_list_display = ()
    show_cancel = True
    ordering = ("name",)
    list_per_page = 20

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
        (
            "Contact",
            {
                "fields": (
                    "contact_name",
                    "contact_tel",
                    "contact_email",
                )
            },
        ),
    )

    search_fields = ["id", "name", "contact_name"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + (
                "name",
                "display_name",
            )
        return self.readonly_fields
