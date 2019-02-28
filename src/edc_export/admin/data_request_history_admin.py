from django.contrib import admin

from ..admin_site import edc_export_admin
from ..models import DataRequestHistory


@admin.register(DataRequestHistory, site=edc_export_admin)
class DataRequestHistoryAdmin(admin.ModelAdmin):

    date_hierarchy = "exported_datetime"

    fields = (
        "data_request",
        "archive_filename",
        "emailed_to",
        "emailed_datetime",
        "summary",
        "exported_datetime",
    )

    list_display = (
        "data_request",
        "emailed_to",
        "emailed_datetime",
        "exported_datetime",
    )

    list_filter = ("emailed_to", "emailed_datetime", "exported_datetime")

    readonly_fields = (
        "data_request",
        "archive_filename",
        "emailed_to",
        "emailed_datetime",
        "summary",
        "exported_datetime",
    )

    search_fields = ("summary", "archive_filename")


class DataRequestHistoryInline(admin.TabularInline):

    model = DataRequestHistory

    fields = ("archive_filename", "emailed_to", "emailed_datetime", "exported_datetime")

    list_display = ("emailed_to", "exported_datetime", "created")

    readonly_fields = (
        "data_request",
        "archive_filename",
        "emailed_to",
        "emailed_datetime",
        "summary",
        "exported_datetime",
    )

    extra = 0
