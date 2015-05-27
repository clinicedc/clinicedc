from django.contrib import admin

from ..models import ExportReceipt


class ExportReceiptAdmin (admin.ModelAdmin):

    date_hierarchy = 'received_datetime'
    list_display = ('export_uuid', 'app_label', 'object_name', 'timestamp', 'received_datetime')
    list_filter = ('app_label', 'object_name', 'received_datetime', 'created', 'modified')
    search_fields = ('export_uuid', 'tx_pk', 'id')

admin.site.register(ExportReceipt, ExportReceiptAdmin)
