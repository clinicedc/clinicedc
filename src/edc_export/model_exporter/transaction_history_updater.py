import json

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from ..constants import EXPORTED, INSERT, UPDATE
from .json_encoder import JSONEncoder


class TransactionHistoryUpdater:

    history_model = 'edc_export.exportedtransaction'

    @property
    def model_cls(self):
        return django_apps.get_model(self.history_model)

    def update(self, row=None, exported_datetime=None):
        try:
            self.model_cls.objects.get(tx_pk=row.get('id'))
        except ObjectDoesNotExist:
            export_change_type = INSERT
        except MultipleObjectsReturned:
            export_change_type = UPDATE
        else:
            export_change_type = UPDATE
        return self.model_cls.objects.create(
            tx=json.dumps(row, cls=JSONEncoder),
            export_uuid=row.get('export_uuid'),
            model=self.model_cls._meta.label_lower,
            tx_pk=row.get('id'),
            exported_datetime=exported_datetime,
            timestamp=exported_datetime.strftime('%Y%m%d%H%M%S'),
            status=EXPORTED,
            exported=True,
            export_change_type=export_change_type)
