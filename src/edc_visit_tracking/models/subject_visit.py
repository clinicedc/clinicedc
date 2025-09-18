from django.db import models
from django.db.models import PROTECT
from django.utils.translation import gettext_lazy as _

from edc_appointment.utils import get_appointment_model_name
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_metadata.model_mixins.creates import CreatesMetadataModelMixin
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.managers import CurrentSiteManager
from edc_sites.model_mixins import SiteModelMixin
from edc_visit_tracking.choices import (
    VISIT_INFO_SOURCE,
    VISIT_REASON,
    VISIT_REASON_MISSED,
)
from edc_visit_tracking.managers import VisitModelManager
from edc_visit_tracking.model_mixins import VisitModelMixin


class SubjectVisit(
    VisitModelMixin,
    CreatesMetadataModelMixin,
    SiteModelMixin,
    RequiresConsentFieldsModelMixin,
    BaseUuidModel,
):
    appointment = models.OneToOneField(
        get_appointment_model_name(),
        on_delete=PROTECT,
        related_name="default_subjectvisit",
    )

    reason = models.CharField(max_length=25, choices=VISIT_REASON)

    reason_missed = models.CharField(
        verbose_name=_("If 'missed', provide the reason for the missed visit"),
        max_length=35,
        choices=VISIT_REASON_MISSED,
        blank=True,
        default="",
    )

    info_source = models.CharField(
        verbose_name=_("What is the main source of this information?"),
        max_length=25,
        choices=VISIT_INFO_SOURCE,
    )

    objects = VisitModelManager()

    on_site = CurrentSiteManager()

    history = HistoricalRecords()

    class Meta(VisitModelMixin.Meta, BaseUuidModel.Meta):
        indexes = (*VisitModelMixin.Meta.indexes, *BaseUuidModel.Meta.indexes)
