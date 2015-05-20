import factory
from datetime import datetime
from edc.base.model.tests.factories import BaseUuidModelFactory
from edc.subject.appointment.tests.factories import AppointmentFactory


class BaseVisitTrackingFactory(BaseUuidModelFactory):
    ABSTRACT_FACTORY = True

    appointment = factory.SubFactory(AppointmentFactory)
    report_datetime = datetime.today()
    reason = 'scheduled'
    reason_missed = None
    info_source = 'subject'
