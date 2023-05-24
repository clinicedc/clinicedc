import csv
import os
import re
from datetime import datetime

from django.db import models
from edc_constants.constants import UUID_PATTERN
from edc_model.models import BaseUuidModel

from .file_history import FileHistory


class UploadExportReceiptFileManager(models.Manager):
    def get_by_natural_key(self, file_name):
        return self.get(file_name=file_name)


class UploadExportReceiptFile(BaseUuidModel):
    export_receipt_file = models.FileField(
        upload_to=os.path.join("media", "edc_export", "uploads")
    )

    file_name = models.CharField(max_length=50, null=True, editable=False, unique=True)

    app_label = models.CharField(max_length=50)

    model_name = models.CharField(max_length=50)

    accepted = models.IntegerField(default=0, editable=False)

    duplicate = models.IntegerField(default=0, editable=False)

    total = models.IntegerField(default=0, editable=False)

    errors = models.TextField(editable=False, null=True)

    receipt_datetime = models.DateTimeField(editable=False, null=True)

    objects = UploadExportReceiptFileManager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.file_name = self.export_receipt_file.name.replace("\\", "/").split("/")[-1]
            self.update_file_history()
        super(UploadExportReceiptFile, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.file_name,)

    def update_file_history(self):
        """Reads the csv file and updates the export history for
        the given export_uuid.
        """
        self.export_receipt_file.open()
        reader = csv.reader(self.export_receipt_file)
        re_pk = re.compile(UUID_PATTERN)
        error_list = []
        for row in reader:
            self.total += 1
            for item in row:
                if re.match(re_pk, item):  # match a row item on uuid
                    if not FileHistory.objects.filter(export_uuid=item):
                        error_list.append(item)
                    elif FileHistory.objects.filter(export_uuid=item, received=True):
                        self.duplicate += 1
                    else:
                        file_history = FileHistory.objects.get(export_uuid=item)
                        file_history.received = True
                        file_history.received_datetime = datetime.today()
                        file_history.save()
                        self.accepted += 1
        self.errors = "; ".join(error_list)

    class Meta:
        ordering = ("-created",)
