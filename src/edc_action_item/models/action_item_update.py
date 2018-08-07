from django.db import models
from django.db.models.deletion import PROTECT
from edc_base import get_utcnow
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel

from .action_item import ActionItem


class ActionItemUpdateManager(models.Manager):

    def get_by_natural_key(self, action_identifier):
        return self.get(action_item__action_identifier=action_identifier)


class ActionItemUpdate(BaseUuidModel):

    action_item = models.ForeignKey(ActionItem, on_delete=PROTECT)

    report_datetime = models.DateTimeField(
        default=get_utcnow)

    comment = models.TextField(
        max_length=250, null=True, blank=True)

    objects = ActionItemUpdateManager()

    history = HistoricalRecords()

    def __str__(self):
        return self.action_item.subject_identifier

    def natural_key(self):
        return self.action_item.natural_key()
    natural_key.dependencies = ['edc_action_item.actionitem']

    @property
    def subject_identifier(self):
        return self.action_item.subject_identifier

    @property
    def action_identifier(self):
        return self.action_item.action_identifier
