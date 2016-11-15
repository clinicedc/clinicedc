from django.core.urlresolvers import reverse
from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_constants.constants import CLOSED

from ..model_mixins import ExportTrackingFieldsMixin


class ExportTransactionManager(models.Manager):

    def get_by_natural_key(self, export_uuid):
        return self.get(export_uuid=export_uuid)


class ExportTransaction(ExportTrackingFieldsMixin, BaseUuidModel):

    tx = models.TextField()

    app_label = models.CharField(
        max_length=64)

    model_name = models.CharField(
        max_length=64)

    tx_pk = models.CharField(
        max_length=36)

    timestamp = models.CharField(
        max_length=50,
        null=True,
        db_index=True)

    status = models.CharField(
        max_length=15,
        default='new',
        choices=(
            ('new', 'New'),
            ('exported', 'Exported'),
            (CLOSED, 'Closed'),
            ('cancelled', 'Cancelled')),
        help_text='exported by export_transactions, closed by import_receipts')

    received = models.BooleanField(
        default=False,
        help_text='True if ACK received')

    received_datetime = models.DateTimeField(
        null=True,
        help_text='date ACK received')

    is_ignored = models.BooleanField(
        default=False,
        help_text='Ignore if update')

    is_error = models.BooleanField(
        default=False)

    objects = ExportTransactionManager()

    history = HistoricalRecords()

    def __str__(self):
        return '{} {} {}'.format(self.model_name, self.status, self.export_uuid)

    def natural_key(self):
        return (self.export_uuid, )

    def render(self):
        url = reverse('view_transaction_url',
                      kwargs={'app_label': self._meta.app_label,
                              'model_name': self._meta.model_name.lower(),
                              'pk': self.pk})
        ret = ('<a href="{url}" class="add-another" id="add_id_report" onclick="return '
               'showAddAnotherPopup(this);"> <img src="/static/admin/img/icon_addlink.gif" '
               'width="10" height="10" alt="View transaction"/></a>').format(url=url)
        return ret
    render.allow_tags = True

    class Meta:
        app_label = 'edc_export'
        ordering = ('-timestamp', )
