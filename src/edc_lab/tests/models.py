from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_mixins import BaseUuidModel
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin

from ..models import RequisitionIdentifierMixin, RequisitionModelMixin
from ..models import RequisitionStatusMixin
from edc_base.utils import get_utcnow
from edc_base.sites.site_model_mixin import SiteModelMixin


class SimpleSubjectVisitManager(models.Manager):
    def get_by_natural_key(self, subject_identifier, report_datetime):
        return self.get(subject_identifier=subject_identifier,
                        report_datetime=report_datetime)


class SubjectRequisitionManager(models.Manager):
    def get_by_natural_key(self, requisition_identifier, subject_identifier,
                           report_datetime):
        subject_visit = SimpleSubjectVisit.objects.get(
            subject_identifier=subject_identifier, report_datetime=report_datetime)
        return self.get(requisition_identifier=requisition_identifier,
                        subject_visit=subject_visit)


class SimpleSubjectVisit(NonUniqueSubjectIdentifierFieldMixin,
                         SiteModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)

    objects = SimpleSubjectVisitManager()

    def natural_key(self):
        return (self.subject_identifier, self.report_datetime)
    natural_key.dependencies = ['sites.Site']


class SubjectRequisition(RequisitionModelMixin,
                         RequisitionStatusMixin,
                         RequisitionIdentifierMixin,
                         BaseUuidModel):

    subject_visit = models.ForeignKey(SimpleSubjectVisit, on_delete=PROTECT)

    objects = SubjectRequisitionManager()

    def natural_key(self):
        return (self.requisition_identifier, ) + self.subject_visit.natural_key()
    natural_key.dependencies = ['edc_lab.simplsubjectvisit', 'sites.Site']

    @property
    def visit(self):
        return self.subject_visit

    @property
    def subject_identifier(self):
        return self.visit.subject_identifier
