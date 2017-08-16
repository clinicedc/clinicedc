import csv

from django.apps import apps as django_apps
from edc_base.utils import get_utcnow


class ExportHistoryUpdater:

    export_history_model = 'edc_export.exporthistory'

    def __init__(self, model=None, filename=None, notification_plan_name=None,
                 path=None, delimiter=None):
        self.model = model
        self.filename = filename
        self.notification_plan_name = notification_plan_name
        self.path = path
        self.delimiter = delimiter

    @property
    def model_cls(self):
        return django_apps.get_model(self.export_history_model)

    def update(self):
        exported_pks = []
        export_uuids = []
        with open(self.path, 'r') as f:
            csv_reader = csv.DictReader(f, delimiter=self.delimiter)
            for row in csv_reader:
                exported_pks.append(row['id'])
                export_uuids.append(row['export_uuid'])
        return self.model_cls.objects.create(
            model=self.model,
            pk_list='|'.join(exported_pks),
            export_uuid_list='|'.join(export_uuids),
            exported=True,
            exported_datetime=get_utcnow(),
            filename=self.filename,
            notification_plan_name=self.notification_plan_name)
