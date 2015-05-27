from datetime import datetime

from django.db import models
from django.core import serializers

from edc.core.crypto_fields.classes import FieldCryptor

from edc_export import ExportTransaction


class ExportHistoryManager(models.Manager):

    export_transaction_model = ExportTransaction
# see https://github.com/treyhunner/django-simple-history/ for some ideas to improve this
#     def __init__(self, model, instance=None):
#         super(ExportHistoryManager, self).__init__()
#         self.model = model
#         self.instance = instance
#
#     def get_query_set(self):
#         if self.instance is None:
#             return super(ExportHistoryManager, self).get_query_set()
#         return super(ExportHistoryManager, self).get_query_set().filter(**{'instance_pk': self.instance.pk})

    def serialize_to_export_transaction(self, instance, change_type, using, encrypt=True, force_export=False):
        """Serialize this instance to the edc_export transaction model if ready.

        Be sure to inspect model property ready_to_export_transaction. ready_to_export_transaction can
        return True or False. If False, the tx will not be exported.

        if model method :func:`ready_to_export_transaction` has not been defined,
        edc_export will proceed.

        .. note:: If change_type == 'D', entire tx is still sent."""
        try:
            ready_to_export_transaction = force_export or instance.ready_to_export_transaction
        except AttributeError as attribute_error:
            if str(attribute_error).endswith("has no attribute 'ready_to_export_transaction'"):
                ready_to_export_transaction = True
            else:
                raise
        if ready_to_export_transaction:
            if instance._meta.proxy_for_model:  # if this is a proxy model, get to the main model
                instance = instance._meta.proxy_for_model.objects.get(id=instance.id)
            json_tx = serializers.serialize("json", [instance, ], ensure_ascii=False, use_natural_keys=False)
            if encrypt:
                json_tx = FieldCryptor('aes', 'local').encrypt(json_tx)
            return ExportTransaction.objects.using(using).create(
                app_label=instance._meta.app_label,
                object_name=instance._meta.object_name,
                tx_pk=instance.id,
                export_change_type=change_type,
                exported=False,
                export_uuid=instance.export_uuid,
                status='new',
                tx=json_tx,
                timestamp=datetime.today().strftime('%Y%m%d%H%M%S%f'),
                )
