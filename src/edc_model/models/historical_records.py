import uuid

from django.db import models
from simple_history.models import HistoricalRecords as SimpleHistoricalRecords


class SerializableModelManager(models.Manager):
    def get_by_natural_key(self, history_id):
        return self.get(history_id=history_id)


class SerializableModel(models.Model):
    objects = SerializableModelManager()

    def natural_key(self) -> tuple:
        return (self.history_id,)  # noqa

    def related_visit_model_attr(self):
        try:
            return self.history_object.related_visit_model_attr()
        except AttributeError:
            raise

    @property
    def related_visit(self):
        return getattr(self, self.related_visit_model_attr())

    class Meta:
        abstract = True


class SerializableCrfModel(models.Model):
    objects = SerializableModelManager()

    @property
    def related_visit(self):
        return NotImplemented(self)

    def natural_key(self) -> tuple:
        return (self.history_id,)  # noqa

    class Meta:
        abstract = True


class HistoricalRecords(SimpleHistoricalRecords):
    """HistoricalRecords that forces a UUID primary key,
    has a natural key method available for serialization,
    and respects \'using\'.
    """

    model_cls = SerializableModel

    def __init__(self, **kwargs):
        """Defaults use of UUIDField instead of AutoField and
        serializable base.
        """
        kwargs.update(bases=(self.model_cls,))
        kwargs.update(history_id_field=models.UUIDField(default=uuid.uuid4))
        kwargs.update(use_base_model_db=True)
        super().__init__(**kwargs)

    def contribute_to_class(self, cls, name):
        try:
            cls.related_visit_model_attr
        except AttributeError:
            pass
        else:
            self.model_cls = SerializableCrfModel
        return super().contribute_to_class(cls, name)
