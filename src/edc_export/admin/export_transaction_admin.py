from django.contrib import admin

from ..models import ExportTransaction

from ..actions import export_as_csv_action, export_tx_to_csv_action


class ExportTransactionAdmin (admin.ModelAdmin):

    date_hierarchy = 'created'
    list_display = (
        'export_uuid', 'timestamp', 'render', 'status',
        'app_label', 'object_name', 'export_change_type',
        'exported', 'received', 'received_datetime', 'created',)
    list_filter = (
        'status', 'exported', 'received', 'app_label',
        'object_name', 'export_change_type', 'received_datetime',
        'created')
    search_fields = ('export_uuid', 'tx_pk', 'tx')

    def get_actions(self, request):
        actions = super(ExportTransactionAdmin, self).get_actions(request)
        actions['export_as_csv_action'] = (
            export_as_csv_action(),
            'export_as_csv_action',
            "Export to CSV")
        actions['export_tx_to_csv_action'] = (
            export_tx_to_csv_action(),
            'export_tx_to_csv_action',
            "Export transaction in selected objects to CSV")
        return actions


admin.site.register(ExportTransaction, ExportTransactionAdmin)
