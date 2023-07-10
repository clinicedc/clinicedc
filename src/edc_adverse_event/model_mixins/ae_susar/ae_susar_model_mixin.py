from django.db import models
from edc_action_item.managers import (
    ActionIdentifierModelManager,
    ActionIdentifierSiteManager,
)
from edc_action_item.models import ActionModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import ReportStatusModelMixin
from edc_sites.models import SiteModelMixin

from edc_adverse_event.constants import AE_SUSAR_ACTION

from .ae_susar_fields_model_mixin import AeSusarFieldsModelMixin
from .ae_susar_methods_model_mixin import AeSusarMethodsModelMixin


class AeSusarModelMixin(
    AeSusarMethodsModelMixin,
    SiteModelMixin,
    ActionModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    AeSusarFieldsModelMixin,
    ReportStatusModelMixin,
    models.Model,
):
    action_name = AE_SUSAR_ACTION

    objects = ActionIdentifierModelManager()

    on_site = ActionIdentifierSiteManager()

    class Meta:
        abstract = True
        verbose_name = "AE SUSAR Report"
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
