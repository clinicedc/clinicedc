import csv
from pathlib import Path

from django.apps import apps as django_apps
from django.utils import timezone


class FileHistoryUpdater:
    file_history_model = "edc_export.filehistory"

    def __init__(
        self,
        path: Path,
        delimiter: str,
        model: str,
        filename: str,
        notification_plan_name: str | None = None,
    ):
        self.model = model
        self.filename = filename
        self.notification_plan_name = notification_plan_name or "Notification plan"
        self.path = path
        self.delimiter = delimiter

    @property
    def model_cls(self):
        return django_apps.get_model(self.file_history_model)

    def update(self):
        exported_pks = []
        export_uuids = []
        with self.path.open("r") as f:
            csv_reader = csv.DictReader(f, delimiter=self.delimiter)
            for row in csv_reader:
                exported_pks.append(row["id"])
                export_uuids.append(row["export_uuid"])
        return self.model_cls.objects.create(
            model=self.model,
            pk_list="|".join(exported_pks),
            export_uuid_list="|".join(export_uuids),
            exported=True,
            exported_datetime=timezone.now(),
            filename=self.filename,
            notification_plan_name=self.notification_plan_name,
        )
