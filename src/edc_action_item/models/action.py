from django.db import models
from django.db.models.deletion import PROTECT
from edc_base import get_utcnow
from edc_base.model_mixins import BaseUuidModel

from .action_type import ActionType
from .action_model_mixin import ActionModelMixin


class Action(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = ''

    action_identifier = models.CharField(
        max_length=25,
        unique=True)

    report_datetime = models.DateTimeField(
        default=get_utcnow)

    action_type = models.ForeignKey(
        ActionType, on_delete=PROTECT,
        related_name='action',
        verbose_name='Action')
