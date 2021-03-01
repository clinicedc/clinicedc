import uuid

from django.db import models
from simple_history.models import HistoricalRecords as SimpleHistoricalRecords


class SerializableModelManager(models.Manager):
    def get_by_natural_key(self, history_id):
        return self.get(history_id=history_id)


class SerializableModel(models.Model):
    objects = SerializableModelManager()

    def natural_key(self) -> tuple:
        return tuple(
            self.history_id,
        )

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
