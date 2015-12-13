from datetime import datetime

from django.db import models

from edc_base.model.models import BaseUuidModel


class ExportHistory(BaseUuidModel):

    app_label = models.CharField(max_length=50)

    object_name = models.CharField(max_length=50)

    export_uuid_list = models.TextField(
        null=True, help_text='list of export_uuid\'s of model app_label.object_name')

    pk_list = models.TextField(
        null=True, help_text='list of pk\'s of model app_label.object_name')

    exit_message = models.CharField(
        max_length=250, help_text='exit message from the export_transactions command')

    exit_status = models.IntegerField(
        null=True, help_text='0=success, 1=failed from the export_transactions command')

    export_filename = models.CharField(
        max_length=250, help_text='original filename on export')

    export_file_contents = models.TextField(
        null=True, help_text='save contents of file as a list of rows')

    exported = models.BooleanField(
        default=False, help_text="exported to a file")

    exported_datetime = models.DateTimeField(null=True)

    notification_plan_name = models.CharField(max_length=50, null=True)

    sent = models.BooleanField(
        default=False, help_text='export file sent to recipient')

    sent_datetime = models.DateTimeField(null=True)

    received = models.BooleanField(
        default=False, help_text='have received an ACK from the recipient')

    received_datetime = models.DateTimeField(null=True)

    closed = models.BooleanField(default=False, help_text='exported, sent, received')

    closed_datetime = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if self.sent and self.received and self.exported and not self.closed:
            self.closed = True
            self.closed_datetime = datetime.now()
        super(ExportHistory, self).save(*args, **kwargs)

    class Meta:
        app_label = 'export'
        ordering = ('-sent_datetime', )
