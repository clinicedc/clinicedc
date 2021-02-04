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

from edc_adverse_event.constants import AE_SUSAR_ACTION

from .ae_susar_fields_model_mixin import AeSusarFieldsModelMixin
from .ae_susar_methods_model_mixin import AeSusarMethodsModelMixin


class AeSusarModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    AeSusarFieldsModelMixin,
    AeSusarMethodsModelMixin,
    ReportStatusModelMixin,
    SiteModelMixin,
    ActionModelMixin,
    TrackingModelMixin,
    models.Model,
):

    action_name = AE_SUSAR_ACTION

    tracking_identifier_prefix = "AS"

    on_site = ActionIdentifierSiteManager()

    objects = ActionIdentifierManager()

    class Meta:
        abstract = True
        verbose_name = "AE SUSAR Report"
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
