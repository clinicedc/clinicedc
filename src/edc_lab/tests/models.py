from edc_base.utils import get_utcnow
__all__ = ['SubjectVisit', 'SubjectRequisition']

from django.db import models

from edc_base.model_mixins import BaseUuidModel
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_lab.model_mixins.requisition import RequisitionModelMixin, RequisitionStatusMixin, RequisitionIdentifierMixin


class SubjectVisit(NonUniqueSubjectIdentifierFieldMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)


class SubjectRequisition(RequisitionModelMixin,
                         RequisitionStatusMixin,
                         RequisitionIdentifierMixin,
                         BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit)
