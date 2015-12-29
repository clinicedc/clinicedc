from lis.exim.lab_import.models import BaseImportHistoryModel


class ImportHistoryModel(BaseImportHistoryModel):

    class Meta:
        app_label = 'lab_clinic_api'
