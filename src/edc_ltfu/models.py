from django.db import models
from edc_action_item.models.action_model_mixin import ActionModelMixin
from edc_identifier.model_mixins import (
    NonUniqueSubjectIdentifierFieldMixin,
    TrackingModelMixin,
)
from edc_model import models as edc_models
from edc_sites.models import SiteModelMixin

from .constants import LTFU_ACTION
from .model_mixins import LtfuModelMixin


class Ltfu(
    NonUniqueSubjectIdentifierFieldMixin,
    LtfuModelMixin,
    SiteModelMixin,
    ActionModelMixin,
    TrackingModelMixin,
    edc_models.BaseUuidModel,
):

    action_name = LTFU_ACTION

    tracking_identifier_prefix = "LF"

    class Meta:
        verbose_name = "Loss to Follow Up"
        verbose_name_plural = "Loss to Follow Ups"
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
