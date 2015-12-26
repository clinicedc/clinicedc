import factory

from django.utils import timezone

from edc_appointment.models import PreAppointmentContact

from .appointment_factory import AppointmentFactory


class PreAppointmentContactFactory(factory.DjangoModelFactory):
    class Meta:
        model = PreAppointmentContact

    appointment = factory.SubFactory(AppointmentFactory)
    contact_datetime = timezone.now()
    is_contacted = 'Yes'
    is_confirmed = True
