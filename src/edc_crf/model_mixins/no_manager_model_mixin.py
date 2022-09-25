from django.conf import settings
from django.db import models
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_metadata.model_mixins.updates import UpdatesCrfMetadataModelMixin
from edc_offstudy.model_mixins import OffstudyCrfModelMixin
from edc_reference.model_mixins import ReferenceModelMixin
from edc_sites.models import SiteModelMixin
from edc_visit_schedule.model_mixins import CrfScheduleModelMixin
from edc_visit_tracking.model_mixins import PreviousVisitModelMixin


class NoManagerModelMixin(
    CrfScheduleModelMixin,
    RequiresConsentFieldsModelMixin,
    PreviousVisitModelMixin,
    UpdatesCrfMetadataModelMixin,
    OffstudyCrfModelMixin,
    SiteModelMixin,
    ReferenceModelMixin,
    models.Model,
):
    """Base model for scheduled CRF models"""

    def natural_key(self) -> tuple:
        return self.related_visit.natural_key()

    natural_key.dependencies = [
        settings.SUBJECT_VISIT_MODEL,
        "sites.Site",
        "edc_appointment.appointment",
    ]

    class Meta:
        abstract = True
