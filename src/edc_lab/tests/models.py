from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin

from ..models import RequisitionIdentifierMixin, RequisitionModelMixin
from ..models import RequisitionStatusMixin


class SubjectVisit(NonUniqueSubjectIdentifierFieldMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)


class SubjectRequisition(RequisitionModelMixin,
                         RequisitionStatusMixin,
                         RequisitionIdentifierMixin,
                         BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    @property
    def visit(self):
        return self.subject_visit

    @property
    def subject_identifier(self):
        return self.visit.subject_identifier
