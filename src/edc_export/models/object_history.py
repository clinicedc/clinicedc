from django.db import models
from django.urls import reverse
from django_crypto_fields.fields import EncryptedTextField
from edc_constants.constants import CLOSED, NEW
from edc_model.models import BaseUuidModel, HistoricalRecords

from ..constants import CANCELLED, EXPORTED
from ..model_mixins import ExportTrackingFieldsModelMixin


class ObjectHistoryManager(models.Manager):
    def get_by_natural_key(self, export_uuid):
        return self.get(export_uuid=export_uuid)


class ObjectHistory(ExportTrackingFieldsModelMixin, BaseUuidModel):
    model = models.CharField(max_length=64)

    tx_pk = models.UUIDField()

    tx = EncryptedTextField()

    exported_datetime = models.DateTimeField()

    timestamp = models.CharField(max_length=50, null=True, db_index=True)

    status = models.CharField(
        max_length=15,
        default=NEW,
        choices=(
            (NEW, "New"),
            (EXPORTED, "Exported"),
            (CLOSED, "Closed"),
            (CANCELLED, "Cancelled"),
        ),
        help_text="exported by export_transactions, closed by import_receipts",
    )

    received = models.BooleanField(default=False, help_text="True if ACK received")

    received_datetime = models.DateTimeField(null=True, help_text="date ACK received")

    is_ignored = models.BooleanField(default=False, help_text="Ignore if update")

    is_error = models.BooleanField(default=False)

    objects = ObjectHistoryManager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.model_name} {self.status} {self.export_uuid}"

    def natural_key(self):
        return (self.export_uuid,)

    def render(self):
        url = reverse(
            "view_transaction_url",
            kwargs={
                "app_label": self._meta.app_label,
                "model_name": self._meta.model_name.lower(),
                "pk": self.pk,
            },
        )
        ret = (
            f'<a href="{url}" class="add-another" id="add_id_report" onclick="return '
            'showAddAnotherPopup(this);"> <img src="/static/admin/img/icon_addlink.gif" '
            'width="10" height="10" alt="View transaction"/></a>'
        )
        return ret

    render.allow_tags = True

    class Meta:
        ordering = ("-timestamp",)
