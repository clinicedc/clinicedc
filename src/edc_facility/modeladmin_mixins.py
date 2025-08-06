from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class HealthFacilityModelAdminMixin:
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "report_datetime",
                    "name",
                    "health_facility_type",
                    "health_facility_type_other",
                )
            },
        ),
        (
            "Clinic days",
            {"fields": ("mon", "tue", "wed", "thu", "fri", "sat")},
        ),
        (
            "Location",
            {
                "description": "Provide this information if available",
                "fields": (
                    "gps",
                    "latitude",
                    "longitude",
                ),
            },
        ),
        (
            "Notes",
            {
                "fields": ("notes",),
            },
        ),
    )

    list_display = (
        "facility_name",
        "health_facility_type",
        "clinic_days",
        "map",
    )

    list_filter = (
        "report_datetime",
        "health_facility_type",
    )

    radio_fields = {
        "health_facility_type": admin.VERTICAL,
    }

    search_fields = (
        "name",
        "health_facility_type__name",
    )

    @admin.display(description="Name", ordering="name")
    def facility_name(self, obj=None):
        return format_html(
            '<span style="white-space:nowrap;">{name}</span>',
            name=obj.name,
        )

    @admin.display(description="Map")
    def map(self, obj=None):
        if obj.latitude and obj.longitude:
            return format_html(
                '<A href="{url}@{latitude},{longitude},15z">'
                '<i class="fas fa-location-dot"></i>',
                url=mark_safe("https://www.google.com/maps/"),  # nosec B703, B308
                latitude=obj.latitude,
                longitude=obj.longitude,
            )
        return None

    @admin.display(description="Days")
    def clinic_days(self, obj=None) -> str:
        return format_html(
            '<span style="white-space:nowrap;">{clinic_days_str}</span>',
            clinic_days_str=obj.clinic_days_str,
        )
