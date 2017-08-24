from django.contrib import admin

from ..admin_site import edc_export_admin
from ..models import FileHistory


@admin.register(FileHistory, site=edc_export_admin)
class FileHistoryAdmin (admin.ModelAdmin):

    date_hierarchy = 'sent_datetime'
    list_display = (
        'model', 'exit_status', 'closed',
        'closed_datetime', 'exported', 'exported_datetime',
        'sent', 'sent_datetime', 'received', 'received_datetime')
    list_filter = (
        'exit_status', 'model', 'closed',
        'sent', 'received', 'exported', 'closed_datetime',
        'exported_datetime', 'sent_datetime', 'received_datetime', 'user_created')
    search_fields = ('export_uuid_list', 'pk_list')
