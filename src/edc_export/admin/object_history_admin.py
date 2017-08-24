from django.contrib import admin

from ..admin_site import edc_export_admin
from ..models import ObjectHistory


@admin.register(ObjectHistory, site=edc_export_admin)
class ObjectHistoryAdmin (admin.ModelAdmin):

    date_hierarchy = 'created'
    list_display = (
        'export_uuid', 'timestamp', 'render', 'status',
        'model', 'export_change_type',
        'exported', 'received', 'received_datetime', 'created',)
    list_filter = (
        'status', 'exported', 'received', 'model',
        'export_change_type', 'received_datetime',
        'created')
    search_fields = ('export_uuid', 'tx_pk', 'tx')
