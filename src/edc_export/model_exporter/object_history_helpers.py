from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core import serializers
from edc_base.utils import get_utcnow
from edc_constants.constants import NEW

from ..constants import EXPORTED, INSERT, UPDATE


class ObjectHistoryUpdaterError(Exception):
    pass


class Base:

    history_model = 'edc_export.objecthistory'

    @property
    def model_cls(self):
        return django_apps.get_model(self.history_model)


class ObjectHistoryCreator(Base):

    def create(self, model_obj=None, change_type=None, using=None):
        if not change_type:
            change_type = self.get_change_type(model_obj=model_obj)
        export_datetime = get_utcnow()
        if model_obj._meta.proxy_for_model:  # if proxy model, get main model
            model_obj = model_obj._meta.proxy_for_model.objects.get(
                id=model_obj.id)
        obj = self.model_cls.objects.using(using).create(
            model=model_obj._meta.label_lower,
            tx_pk=model_obj.id,
            export_change_type=change_type,
            exported=False,
            export_uuid=model_obj.export_uuid,
            status=NEW,
            tx=self.get_json_tx(model_obj),
            exported_datetime=export_datetime,
            timestamp=export_datetime.strftime('%Y%m%d%H%M%S%f'))
        return obj

    def get_json_tx(self, model_obj=None):
        return serializers.serialize(
            "json", [model_obj, ],
            ensure_ascii=True,
            use_natural_foreign_keys=True,
            use_natural_primary_keys=False)

    def get_change_type(self, model_obj=None):
        """Returns the export_change_type by querying the
        object history model for existing instances.
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


class ObjectHistoryGetter(Base):

    object_creator = ObjectHistoryCreator()

    def get_not_exported(self, model_obj=None, create=None):
        """Returns a queryset of objecthistory objects
        not yet exported.
        """
        try:
            self.model_cls.objects.get(export_uuid=model_obj.export_uuid)
        except ObjectDoesNotExist:
            if create:
                self.object_creator.create(model_obj=model_obj)
        except MultipleObjectsReturned:
            pass
        return self.model_cls.objects.filter(
            export_uuid=model_obj.export_uuid,
            exported=False).order_by('created')


class ObjectHistoryUpdater(Base):

    def update_as_exported(self, objects=None, exported_datetime=None):
        """Updates all objects in the objecthistory queryset
        as exported.
        """
        for obj in objects:
            if obj.exported:
                raise ObjectHistoryUpdaterError(
                    f'Already exported. Got {objects}.')
        objects.update(
            exported=True,
            status=EXPORTED,
            exported_datetime=exported_datetime,
            timestamp=exported_datetime.strftime('%Y%m%d%H%M%S'))


class ObjectHistoryHelper:

    obj_getter = ObjectHistoryGetter()
    obj_updater = ObjectHistoryUpdater()

    def __init__(self, model_obj=None, create=None):
        self.model_obj = model_obj
        self.create = create

    def get_not_exported(self):
        return self.obj_getter.get_not_exported(
            model_obj=self.model_obj, create=self.create)

    def update_as_exported(self, **kwargs):
        self.obj_updater.update_as_exported(**kwargs)
