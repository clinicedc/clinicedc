from django.db import models
from edc_appointment.model_mixins import AppointmentModelMixin
from edc_base.model_mixins import BaseUuidModel
from edc_search.model_mixins import SearchSlugManager

from .search_slug_model_mixin import SearchSlugModelMixin


class Manager(SearchSlugManager, models.Manager):
    pass


class Appointment(SearchSlugModelMixin, AppointmentModelMixin, BaseUuidModel):

    objects = Manager()

    def __str__(self):
        return (f'{self.appt_datetime} - {self.profile_label}')
