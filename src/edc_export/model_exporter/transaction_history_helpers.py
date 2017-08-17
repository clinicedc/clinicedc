from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core import serializers
from edc_base.utils import get_utcnow
from edc_constants.constants import NEW

from ..constants import EXPORTED, INSERT, UPDATE


class TransactionHistoryUpdaterError(Exception):
    pass


class Base:

    history_model = 'edc_export.exportedtransaction'

    @property
    def model_cls(self):
        return django_apps.get_model(self.history_model)


class TransactionHistoryCreator(Base):

    def create(self, model_obj=None, change_type=None, using=None):
        if not change_type:
            change_type = self.get_change_type(model_obj=model_obj)
        export_datetime = get_utcnow()
        if model_obj._meta.proxy_for_model:  # if proxy model, get main model
            model_obj = model_obj._meta.proxy_for_model.objects.get(
                id=model_obj.id)
        tx_obj = self.model_cls.objects.using(using).create(
            model=model_obj._meta.label_lower,
            tx_pk=model_obj.id,
            export_change_type=change_type,
            exported=False,
            export_uuid=model_obj.export_uuid,
            status=NEW,
            tx=self.get_json_tx(model_obj),
            exported_datetime=export_datetime,
            timestamp=export_datetime.strftime('%Y%m%d%H%M%S%f'))
        return tx_obj

    def get_json_tx(self, model_obj=None):
        return serializers.serialize(
            "json", [model_obj, ],
            ensure_ascii=True,
            use_natural_foreign_keys=True,
            use_natural_primary_keys=False)

    def get_change_type(self, model_obj=None):
        """Returns the export_change_type by querying the
        transaction history model for existing instances.
        """
        try:
            self.model_cls.objects.get(export_uuid=model_obj.export_uuid)
        except ObjectDoesNotExist:
            export_change_type = INSERT
        except MultipleObjectsReturned:
            export_change_type = UPDATE
        else:
            export_change_type = UPDATE
        return export_change_type


class TransactionHistoryGetter(Base):

    tx_creator = TransactionHistoryCreator()

    def get_not_exported(self, model_obj=None, create=None):
        """Returns a queryset of transaction history objects
        not yet exported.
        """
        try:
            self.model_cls.objects.get(export_uuid=model_obj.export_uuid)
        except ObjectDoesNotExist:
            if create:
                self.tx_creator.create(model_obj=model_obj)
        except MultipleObjectsReturned:
            pass
        return self.model_cls.objects.filter(
            export_uuid=model_obj.export_uuid,
            exported=False).order_by('created')


class TransactionHistoryUpdater(Base):

    def update_as_exported(self, tx_objects=None, exported_datetime=None):
        """Updates all objects in the transaction history queryset
        as exported.
        """
        for tx_obj in tx_objects:
            if tx_obj.exported:
                raise TransactionHistoryUpdaterError(
                    f'Already exported. Got {tx_obj}.')
        tx_objects.update(
            exported=True,
            status=EXPORTED,
            exported_datetime=exported_datetime,
            timestamp=exported_datetime.strftime('%Y%m%d%H%M%S'))


class TransactionHistoryHelper:

    tx_getter = TransactionHistoryGetter()
    tx_updater = TransactionHistoryUpdater()

    def __init__(self, model_obj=None, create=None):
        self.model_obj = model_obj
        self.create = create

    def get_not_exported(self):
        return self.tx_getter.get_not_exported(
            model_obj=self.model_obj, create=self.create)

    def update_as_exported(self, **kwargs):
        self.tx_updater.update_as_exported(**kwargs)
