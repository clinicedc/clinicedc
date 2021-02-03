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
from edc_search.model_mixins import SearchSlugModelMixin
from edc_sites.models import SiteModelMixin

from ...constants import AE_TMG_ACTION
from .ae_tmg_fields_model_mixin import AeTmgFieldsModelMixin
from .ae_tmg_methods_model_mixin import AeTmgMethodsModelMixin


class AeTmgModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    AeTmgFieldsModelMixin,
    AeTmgMethodsModelMixin,
    ReportStatusModelMixin,
    SearchSlugModelMixin,
    SiteModelMixin,
    ActionModelMixin,
    TrackingModelMixin,
    models.Model,
):

    action_name = AE_TMG_ACTION

    tracking_identifier_prefix = "AT"

    on_site = ActionIdentifierSiteManager()

    objects = ActionIdentifierManager()

    class Meta:
        abstract = True
        verbose_name = "AE TMG Report"
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
