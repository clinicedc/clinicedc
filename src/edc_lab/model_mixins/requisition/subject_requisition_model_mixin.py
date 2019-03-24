from django.apps import apps as django_apps
from django.db import models
from django.db.models.deletion import PROTECT
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_constants.constants import NOT_APPLICABLE
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_metadata.model_mixins.updates import UpdatesRequisitionMetadataModelMixin
from edc_model.models import BaseUuidModel
from edc_model.models import HistoricalRecords
from edc_reference.model_mixins import RequisitionReferenceModelMixin
from edc_search.model_mixins import SearchSlugManager, SearchSlugModelMixin
from edc_visit_schedule.model_mixins import SubjectScheduleCrfModelMixin
from edc_visit_tracking.managers import (
    CrfModelManager as VisitTrackingCrfModelManager,
    CurrentSiteManager,
)
from edc_visit_tracking.model_mixins import CrfModelMixin as VisitTrackingCrfModelMixin
from edc_visit_tracking.model_mixins import PreviousVisitModelMixin
from django.conf import settings

from ...choices import REASON_NOT_DRAWN


from .requisition_identifier_mixin import RequisitionIdentifierMixin
from .requisition_model_mixin import RequisitionModelMixin
from .requisition_status_mixin import RequisitionStatusMixin


class SubjectRequisitionManager(VisitTrackingCrfModelManager, SearchSlugManager):
    pass


class SubjectRequisitionModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    RequisitionModelMixin,
    RequisitionStatusMixin,
    RequisitionIdentifierMixin,
    VisitTrackingCrfModelMixin,
    SubjectScheduleCrfModelMixin,
    RequiresConsentFieldsModelMixin,
    PreviousVisitModelMixin,
    RequisitionReferenceModelMixin,
    UpdatesRequisitionMetadataModelMixin,
    SearchSlugModelMixin,
    BaseUuidModel,
):

    subject_visit = models.ForeignKey(
        settings.SUBJECT_VISIT_MODEL, on_delete=PROTECT)

    reason_not_drawn = models.CharField(
        verbose_name="If not drawn, please explain",
        max_length=25,
        default=NOT_APPLICABLE,
        choices=REASON_NOT_DRAWN,
    )

    on_site = CurrentSiteManager()

    objects = SubjectRequisitionManager()

    history = HistoricalRecords(inherit=True)

    def __str__(self):
        return f"{self.requisition_identifier} " f"{self.panel_object.verbose_name}"

    def save(self, *args, **kwargs):
        if not self.id:
            edc_protocol_app_config = django_apps.get_app_config(
                "edc_protocol")
            self.protocol_number = edc_protocol_app_config.protocol_number
        self.subject_identifier = self.subject_visit.subject_identifier
        super().save(*args, **kwargs)

    def get_search_slug_fields(self):
        fields = super().get_search_slug_fields()
        fields.extend(
            ["subject_identifier",
             "requisition_identifier",
             "human_readable_identifier",
             "identifier_prefix"]
        )
        return fields

    class Meta:
        abstract = True
        unique_together = ("panel", "subject_visit")
