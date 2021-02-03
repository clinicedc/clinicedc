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

from ...constants import AE_FOLLOWUP_ACTION
from .ae_followup_fields_model_mixin import AeFollowupFieldsModelMixin
from .ae_followup_methods_model_mixin import AeFollowupMethodsModelMixin


class AeFollowupModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    AeFollowupFieldsModelMixin,
    AeFollowupMethodsModelMixin,
    SiteModelMixin,
    ActionModelMixin,
    TrackingModelMixin,
    models.Model,
):

    action_name = AE_FOLLOWUP_ACTION

    tracking_identifier_prefix = "AF"

    on_site = ActionIdentifierSiteManager()

    objects = ActionIdentifierManager()

    class Meta:
        abstract = True
        verbose_name = "AE Follow-up Report"
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
