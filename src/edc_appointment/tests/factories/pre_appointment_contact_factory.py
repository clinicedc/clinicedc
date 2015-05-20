import factory
from datetime import datetime
from edc.base.model.tests.factories import BaseUuidModelFactory
from edc_appointment import PreAppointmentContact
from edc_appointment_factory import AppointmentFactory


class PreAppointmentContactFactory(BaseUuidModelFactory):
    FACTORY_FOR = PreAppointmentContact

    appointment = factory.SubFactory(AppointmentFactory)
    contact_datetime = datetime.today()
    is_contacted = 'Yes'
    is_confirmed = True
