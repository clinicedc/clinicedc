from uuid import uuid4

from django.db import models
from django.utils import timezone
from edc_model.models import BaseUuidModel, HistoricalRecords


class FileHistoryManager(models.Manager):
    def get_by_natural_key(self, history_uuid):
        return self.get(history_uuid=history_uuid)


class FileHistory(BaseUuidModel):

    history_uuid = models.UUIDField(
        editable=False,
        default=uuid4,
        unique=True,
        help_text="system field for export tracking.",
    )

    model = models.CharField(max_length=50)

    export_uuid_list = models.TextField(
        null=True, help_text="list of export_uuid's of model app_label.model_name"
    )

    pk_list = models.TextField(
        null=True, help_text="list of pk's of model app_label.model_name"
    )

    exit_message = models.CharField(
        max_length=250, help_text="exit message from the export_transactions command"
    )

    exit_status = models.IntegerField(
        null=True, help_text="0=success, 1=failed from the export_transactions command"
    )

    filename = models.CharField(max_length=250, help_text="original filename on export")

    file_contents = models.TextField(
        null=True, help_text="save contents of file as a list of rows"
    )

    exported = models.BooleanField(default=False, help_text="exported to a file")

    exported_datetime = models.DateTimeField(null=True)

    notification_plan_name = models.CharField(max_length=50, null=True)

    sent = models.BooleanField(default=False, help_text="export file sent to recipient")

    sent_datetime = models.DateTimeField(null=True)

    received = models.BooleanField(
        default=False, help_text="have received an ACK from the recipient"
    )

    received_datetime = models.DateTimeField(null=True)

    closed = models.BooleanField(default=False, help_text="exported, sent, received")

    closed_datetime = models.DateTimeField(null=True)

    objects = FileHistoryManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if self.sent and self.received and self.exported and not self.closed:
            self.closed = True
            self.closed_datetime = timezone.now()
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.history_uuid,)

    class Meta:
        ordering = ("-sent_datetime",)
