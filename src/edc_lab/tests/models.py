from django.db import models
from django.db.models.deletion import PROTECT
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow

from ..model_mixins import (
    RequisitionIdentifierMixin,
    RequisitionModelMixin,
    RequisitionStatusMixin,
)


class SubjectVisitManager(models.Manager):
    def get_by_natural_key(self, subject_identifier, report_datetime):
        return self.get(
            subject_identifier=subject_identifier, report_datetime=report_datetime
        )


class SubjectRequisitionManager(models.Manager):
    def get_by_natural_key(
        self, requisition_identifier, subject_identifier, report_datetime
    ):
        subject_visit = SubjectVisit.objects.get(
            subject_identifier=subject_identifier, report_datetime=report_datetime
        )
        return self.get(
            requisition_identifier=requisition_identifier, subject_visit=subject_visit
        )


class SubjectVisit(
    NonUniqueSubjectIdentifierFieldMixin, SiteModelMixin, BaseUuidModel
):

    report_datetime = models.DateTimeField(default=get_utcnow)

    objects = SubjectVisitManager()

    def natural_key(self):
        return (self.subject_identifier, self.report_datetime)

    natural_key.dependencies = ["sites.Site"]


class SubjectRequisition(
    RequisitionModelMixin,
    RequisitionStatusMixin,
    RequisitionIdentifierMixin,
    BaseUuidModel,
):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    objects = SubjectRequisitionManager()

    def natural_key(self):
        return (self.requisition_identifier,) + self.subject_visit.natural_key()

    natural_key.dependencies = ["edc_lab.simplsubjectvisit", "sites.Site"]

    @property
    def visit(self):
        return self.subject_visit

    @property
    def subject_identifier(self):
        return self.visit.subject_identifier
