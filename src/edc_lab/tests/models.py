__all__ = ['SubjectVisit', 'SubjectRequisition']

from django.db import models

from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_lab.model_mixins.requisition import RequisitionModelMixin
from edc_lab.model_mixins.requisition import RequisitionStatusMixin
from edc_lab.model_mixins.requisition import RequisitionIdentifierMixin


class SubjectVisit(NonUniqueSubjectIdentifierFieldMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)


class SubjectRequisition(RequisitionModelMixin,
                         RequisitionStatusMixin,
                         RequisitionIdentifierMixin,
                         BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit)

    @property
    def visit(self):
        return self.subject_visit

    @property
    def subject_identifier(self):
        return self.visit.subject_identifier
