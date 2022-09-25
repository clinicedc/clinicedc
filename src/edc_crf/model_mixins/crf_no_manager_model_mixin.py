from django.db import models
from edc_visit_tracking.model_mixins import VisitTrackingCrfModelMixin

from .no_manager_model_mixin import NoManagerModelMixin


class CrfNoManagerModelMixin(
    VisitTrackingCrfModelMixin,
    NoManagerModelMixin,
):
    """Modelmixin for all scheduled CRF models"""

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["subject_visit", "site", "id"]),
            models.Index(fields=["subject_visit", "report_datetime"]),
        ]
        default_permissions = ("add", "change", "delete", "view", "export", "import")
