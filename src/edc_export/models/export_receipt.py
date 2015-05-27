# from django.core.urlresolvers import reverse
from django.db import models
from django_extensions.db.fields import UUIDField

from edc_base.model.models import BaseUuidModel
try:
    from edc_sync.mixins import SyncMixin
except ImportError:
    SyncMixin = type('SyncMixin', (object, ), {})


class ExportReceipt(SyncMixin, BaseUuidModel):

    export_uuid = UUIDField(
        editable=False,
        help_text="system field for edc_export tracking.")

    app_label = models.CharField(
        max_length=64,
    )

    object_name = models.CharField(
        max_length=64,
    )

    tx_pk = models.CharField(
        max_length=36,
    )

    timestamp = models.CharField(
        max_length=50,
        null=True,
    )

    received_datetime = models.DateTimeField(
        null=True,
        help_text='date ACK received'
    )

    objects = models.Manager()

    def __unicode__(self):
        return '{} {}'.format(self.object_name, self.export_uuid)

    def dashboard(self):
        # TODO: get this dashboard url
        return 'dashboard?'

    class Meta:
        app_label = 'edc_export'
        ordering = ('-timestamp', )
