from django.conf import settings
from django.db import models
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_metadata.model_mixins.updates import UpdatesCrfMetadataModelMixin
from edc_offstudy.model_mixins import OffstudyCrfModelMixin
from edc_reference.model_mixins import ReferenceModelMixin
from edc_sites.models import SiteModelMixin
from edc_visit_tracking.model_mixins import (
    PreviousVisitModelMixin,
    VisitTrackingCrfModelMixin,
)


class CrfNoManagerModelMixin(
    VisitTrackingCrfModelMixin,
    RequiresConsentFieldsModelMixin,
    PreviousVisitModelMixin,
    UpdatesCrfMetadataModelMixin,
    OffstudyCrfModelMixin,
    SiteModelMixin,
    ReferenceModelMixin,
):
    """Base model for all scheduled models"""

    subject_visit = models.OneToOneField(
        settings.SUBJECT_VISIT_MODEL, on_delete=models.PROTECT
    )

    def natural_key(self) -> tuple:
        return self.subject_visit.natural_key()

    natural_key.dependencies = [  # type:ignore
        settings.SUBJECT_VISIT_MODEL,
        "sites.Site",
        "edc_appointment.appointment",
    ]

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["subject_visit", "site", "id"])]
        default_permissions = ("add", "change", "delete", "view", "export", "import")
