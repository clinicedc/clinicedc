from django.conf import settings
from django.db import models
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_metadata.model_mixins.updates import UpdatesCrfMetadataModelMixin
from edc_offstudy.model_mixins import OffstudyCrfModelMixin
from edc_reference.model_mixins import ReferenceModelMixin
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
    ReferenceModelMixin,
    models.Model,
):
    """Modelmixin for all scheduled CRF models"""

    def natural_key(self) -> tuple:
        return self.related_visit.natural_key()

    natural_key.dependencies = [
        settings.SUBJECT_VISIT_MODEL,
        "sites.Site",
        "edc_appointment.appointment",
    ]

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["subject_visit", "site", "id"]),
            models.Index(fields=["subject_visit", "report_datetime"]),
        ]
        default_permissions = ("add", "change", "delete", "view", "export", "import")
