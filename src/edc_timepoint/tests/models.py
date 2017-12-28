from django.db import models
from django.db.models.deletion import PROTECT

from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_appointment.models import Appointment

from ..model_mixins import TimepointLookupModelMixin
from ..timepoint_lookup import TimepointLookup


class VisitTimepointLookup(TimepointLookup):
    timepoint_model = 'edc_timepoint.appointment'
    timepoint_related_model_lookup = 'appointment'


class CrfTimepointLookup(TimepointLookup):
    timepoint_model = 'edc_timepoint.appointment'


class SubjectVisit(TimepointLookupModelMixin, BaseUuidModel):

    timepoint_lookup_cls = VisitTimepointLookup

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=50)

    report_datetime = models.DateTimeField(default=get_utcnow)

    visit_code = models.CharField(max_length=50)


class CrfOne(TimepointLookupModelMixin, BaseUuidModel):

    timepoint_lookup_cls = CrfTimepointLookup

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)
