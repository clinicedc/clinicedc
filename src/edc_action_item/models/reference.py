from django.db import models
from django.db.models.deletion import PROTECT
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow

from .action_type import ActionType
from .action_model_mixin import ActionModelMixin


class ReferenceManager(models.Manager):
    def get_by_natural_key(self, action_identifier):
        return self.get(action_identifier=action_identifier)


class Reference(ActionModelMixin, BaseUuidModel):

    """Model used as a default reference model for simple actions
    not created by another model.

    Note: In almost all cases an action is created by a model. The
    creating model is then the "reference" model.
    """

    action_identifier = models.CharField(max_length=25, unique=True)

    report_datetime = models.DateTimeField(default=get_utcnow)

    action_type = models.ForeignKey(
        ActionType, on_delete=PROTECT, related_name="action", verbose_name="Action"
    )

    objects = ReferenceManager()

    def natural_key(self):
        return (self.action_identifier,)
