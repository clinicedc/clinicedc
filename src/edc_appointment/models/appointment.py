from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow

from ..managers import AppointmentManager
from ..model_mixins import AppointmentModelMixin


class Appointment(AppointmentModelMixin, BaseUuidModel):

    objects = AppointmentManager()

    history = HistoricalRecords()

    class Meta(AppointmentModelMixin.Meta):
        pass
