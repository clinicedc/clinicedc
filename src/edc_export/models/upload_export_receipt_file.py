import csv
import re
import os

from datetime import datetime

from django.db import models
from django.conf import settings

from edc_base.model.models import BaseUuidModel
from edc_export.models import ExportHistory


class UploadExportReceiptFile(BaseUuidModel):

    export_receipt_file = models.FileField(
        upload_to=os.path.join(settings.BASE_DIR, 'uploads'))

    file_name = models.CharField(
        max_length=50, null=True, editable=False, unique=True)

    app_label = models.CharField(max_length=50)

    object_name = models.CharField(max_length=50)

    accepted = models.IntegerField(default=0, editable=False)

    duplicate = models.IntegerField(default=0, editable=False)

    total = models.IntegerField(default=0, editable=False)

    errors = models.TextField(editable=False, null=True)

    receipt_datetime = models.DateTimeField(editable=False, null=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.file_name = self.export_receipt_file.name.replace('\\', '/').split('/')[-1]
            self.update_export_history()
        super(UploadExportReceiptFile, self).save(*args, **kwargs)

    def update_export_history(self):
        """Reads the csv file and updates the export history for the given export_uuid."""
        self.export_receipt_file.open()
        reader = csv.reader(self.export_receipt_file)
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        error_list = []
        for row in reader:
            self.total += 1
            for item in row:
                if re.match(re_pk, item):  # match a row item on uuid
                    if not ExportHistory.objects.filter(export_uuid=item):
                        error_list.append(item)
                    elif ExportHistory.objects.filter(export_uuid=item, received=True):
                        self.duplicate += 1
                    else:
                        export_history = ExportHistory.objects.get(export_uuid=item)
                        export_history.received = True
                        export_history.received_datetime = datetime.today()
                        export_history.save()
                        self.accepted += 1
        self.errors = '; '.join(error_list)

    class Meta:
        app_label = 'edc_export'
        ordering = ('-created', )
