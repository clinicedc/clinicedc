from django.db import models
from edc_action_item.managers import (
    ActionIdentifierManager,
    ActionIdentifierSiteManager,
)
from edc_action_item.models import ActionModelMixin
from edc_identifier.model_mixins import (
    NonUniqueSubjectIdentifierFieldMixin,
    TrackingModelMixin,
)
from edc_model.models import ReportStatusModelMixin
from edc_sites.models import SiteModelMixin

from edc_adverse_event.constants import AESI_ACTION

from .aesi_fields_model_mixin import AesiFieldsModelMixin
from .aesi_methods_model_mixin import AesiMethodsModelMixin


class AesiModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    AesiFieldsModelMixin,
    AesiMethodsModelMixin,
    ReportStatusModelMixin,
    SiteModelMixin,
    ActionModelMixin,
    TrackingModelMixin,
    models.Model,
):

    action_name = AESI_ACTION

    tracking_identifier_prefix = "AI"

    on_site = ActionIdentifierSiteManager()

    objects = ActionIdentifierManager()

    class Meta:
        abstract = True
        verbose_name = "AE of Special Interest Report"
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
