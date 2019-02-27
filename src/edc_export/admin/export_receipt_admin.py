from django.contrib import admin

from ..admin_site import edc_export_admin
from ..models import ExportReceipt


@admin.register(ExportReceipt, site=edc_export_admin)
class ExportReceiptAdmin(admin.ModelAdmin):

    date_hierarchy = "received_datetime"
    list_display = ("export_uuid", "model", "timestamp", "received_datetime")
    list_filter = ("model", "received_datetime", "created", "modified")
    search_fields = ("export_uuid", "tx_pk", "id")
