from django.db import models
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_visit_schedule.model_mixins import VisitCodeFieldsModelMixin


class Appointment(
    NonUniqueSubjectIdentifierFieldMixin, VisitCodeFieldsModelMixin, BaseUuidModel
):
    class Meta(BaseUuidModel.Meta):
        pass


class SubjectVisit(
    NonUniqueSubjectIdentifierFieldMixin, VisitCodeFieldsModelMixin, BaseUuidModel
):

    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, related_name="+")

    class Meta(BaseUuidModel.Meta):
        pass
