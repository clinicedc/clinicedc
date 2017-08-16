from django.apps import apps as django_apps
from django.core import serializers
from django.db import models
from edc_constants.constants import NEW
from edc_base.utils import get_utcnow


class ExportHistoryManager(models.Manager):

    transaction_history_model = 'edc_export.exportedtransaction'

    @property
    def transaction_history_model_model_cls(self):
        return django_apps.get_model(self.transaction_history_model)

    def serialize_to_export_transaction(self, instance, change_type,
                                        using, force_export=False):
        """Serialize this instance to the export transaction model if ready.

        Be sure to inspect model property ready_to_export_transaction. ready_to_export_transaction can
        return True or False. If False, the tx will not be exported.

        if model method :func:`ready_to_export_transaction` has not been defined,
        export will proceed.

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
                instance = instance._meta.proxy_for_model.objects.get(
                    id=instance.id)
            json_tx = serializers.serialize(
                "json", [instance, ],
                ensure_ascii=True,
                use_natural_foreign_keys=True,
                use_natural_primary_keys=False)
            export_datetime = get_utcnow()
            return self.transaction_history_model_model_cls.objects.using(using).create(
                model=instance._meta.label_lower,
                tx_pk=instance.id,
                export_change_type=change_type,
                exported=False,
                export_uuid=instance.export_uuid,
                status=NEW,
                tx=json_tx,
                exported_datetime=export_datetime,
                timestamp=export_datetime.strftime('%Y%m%d%H%M%S%f'))
