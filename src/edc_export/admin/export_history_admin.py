from django.contrib import admin

from ..actions import export_file_contents
from ..models import ExportHistory


class ExportHistoryAdmin (admin.ModelAdmin):

    date_hierarchy = 'sent_datetime'
    list_display = (
        'object_name', 'app_label', 'exit_status', 'closed',
        'closed_datetime', 'exported', 'exported_datetime',
        'sent', 'sent_datetime', 'received', 'received_datetime')
    list_filter = (
        'exit_status', 'app_label', 'object_name', 'closed',
        'sent', 'received', 'exported', 'closed_datetime',
        'exported_datetime', 'sent_datetime', 'received_datetime', 'user_created')
    search_fields = ('export_uuid_list', 'pk_list')
    actions = [export_file_contents, ]
admin.site.register(ExportHistory, ExportHistoryAdmin)
