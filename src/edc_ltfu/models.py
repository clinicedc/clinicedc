from django.db import models

from edc_action_item.models.action_model_mixin import ActionModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_sites.model_mixins import SiteModelMixin

from .constants import LTFU_ACTION
from .model_mixins import LtfuModelMixin


class Ltfu(
    NonUniqueSubjectIdentifierFieldMixin,
    LtfuModelMixin,
    SiteModelMixin,
    ActionModelMixin,
    BaseUuidModel,
):
    action_name = LTFU_ACTION

    class Meta(BaseUuidModel.Meta, NonUniqueSubjectIdentifierFieldMixin.Meta):
        verbose_name = "Loss to Follow Up"
        verbose_name_plural = "Loss to Follow Ups"
        indexes = (
            *NonUniqueSubjectIdentifierFieldMixin.Meta.indexes,
            *ActionModelMixin.Meta.indexes,
            *BaseUuidModel.Meta.indexes,
            models.Index(fields=["subject_identifier", "action_identifier", "site"]),
        )
