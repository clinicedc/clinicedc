from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_mixins import BaseUuidModel


class Appointment(BaseUuidModel):

    pass


class SubjectVisit(BaseUuidModel):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)
