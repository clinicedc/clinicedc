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
from edc_sites.models import SiteModelMixin

from ...constants import AE_INITIAL_ACTION
from .ae_initial_ae_model_mixin import AeInitialAeModelMixin
from .ae_initial_fields_model_mixin import AeInitialFieldsModelMixin
from .ae_initial_methods_model_mixin import AeInitialMethodsModelMixin
from .ae_initial_sae_model_mixin import AeInitialSaeModelMixin
from .ae_initial_susar_model_mixin import AeInitialSusarModelMixin
from .ae_initial_tmg_model_mixin import AeInitialTmgModelMixin


class AeInitialModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    AeInitialFieldsModelMixin,
    AeInitialMethodsModelMixin,
    AeInitialAeModelMixin,
    AeInitialSaeModelMixin,
    AeInitialSusarModelMixin,
    AeInitialTmgModelMixin,
    SiteModelMixin,
    ActionModelMixin,
    TrackingModelMixin,
    models.Model,
):

    action_name = AE_INITIAL_ACTION

    tracking_identifier_prefix = "AE"

    on_site = ActionIdentifierSiteManager()

    objects = ActionIdentifierManager()

    class Meta:
        abstract = True
        verbose_name = "AE Initial Report"
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
