from clinicedc_constants import NOT_APPLICABLE
from django.db import models

from edc_metadata.model_mixins.creates import CreatesMetadataModelMixin
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_offstudy.model_mixins import OffstudyNonCrfModelMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_visit_tracking.choices import VISIT_REASON
from edc_visit_tracking.managers import VisitCurrentSiteManager
from edc_visit_tracking.managers import VisitModelManager as BaseVisitModelManager
from edc_visit_tracking.model_mixins import VisitModelMixin


class VisitModelManager(BaseVisitModelManager):
    def create_missed_extras(self) -> dict:
        return dict(assessment_type=NOT_APPLICABLE, assessment_who=NOT_APPLICABLE)


class SubjectVisit(
    SiteModelMixin,
    VisitModelMixin,
    CreatesMetadataModelMixin,
    OffstudyNonCrfModelMixin,
    BaseUuidModel,
):
    """A model completed by the user that captures the covering
    information for the data collected for this timepoint/appointment,
    e.g.report_datetime.
    """

    # override default
    reason = models.CharField(
        verbose_name="What is the reason for this visit report?",
        max_length=25,
        choices=VISIT_REASON,
        help_text="If 'missed', fill in the separate missed visit report",
    )

    unschedule_detail = models.TextField(
        verbose_name="If 'unschedule', please provide further details, if any",
        null=True,
        blank=True,
    )

    on_site = VisitCurrentSiteManager()

    objects = VisitModelManager()

    history = HistoricalRecords()

    class Meta(VisitModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Subject Visit"
        verbose_name_plural = "Subject Visits"
