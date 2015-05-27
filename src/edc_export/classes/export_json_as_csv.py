from .base_export_model import BaseExportModel


class ExportJsonAsCsv(BaseExportModel):

    def __init__(self, queryset, model=None, modeladmin=None, fields=None, exclude=None, extra_fields=None,
                 header=True, track_history=False, show_all_fields=True, delimiter=None, encrypt=True, strip=False,
                 target_path=None, notification_plan_name=None, export_datetime=None, remove_duplicates=True):
        self._row_instance = None
        self.export_transaction = None
        self.target_path = target_path
        self.export_datetime = export_datetime
        self.remove_duplicates = remove_duplicates
        super(ExportJsonAsCsv, self).__init__(queryset, model, modeladmin, fields, exclude, extra_fields, header,
                                              track_history, show_all_fields, delimiter, encrypt, strip,
                                              notification_plan_name, export_datetime)

    @property
    def row_instance(self):
        return self._row_instance

    @row_instance.setter
    def row_instance(self, row_instance):
        self._row_instance = row_instance
        if row_instance:
            self._row_instance.export_change_type, self._row_instance.exported_datetime = (self._row_instance.export_transaction.export_change_type, self.export_datetime)

    def update_export_transaction(self, row_instance=None):
        self.row_instance.export_transaction.exported_datetime = self.export_datetime
        self.row_instance.export_transaction.status = 'exported'
        self.row_instance.export_transaction.exported = True
        self.row_instance.export_transaction.save()
