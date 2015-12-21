from django.db import models

from .appointment_mixin import AppointmentMixin


class BaseAppointmentHelperModel(AppointmentMixin, models.Model):

    """ Base for models that may be trigger the creation of appointments
    such as registration models models that need a key to RegisteredSubject.

    Such models may be listed by name in the ScheduledGroup model and thus
    trigger the creation of appointments.

    """

    class Meta:
        abstract = True
