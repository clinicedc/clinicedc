import factory
from datetime import datetime
from edc.base.model.tests.factories import BaseUuidModelFactory
from edc.subject.appointment.tests.factories import AppointmentFactory
from edc_constants.constants import SCHEDULED


class BaseVisitTrackingFactory(BaseUuidModelFactory):

    class Meta:
        abstract = True

    appointment = factory.SubFactory(AppointmentFactory)
    report_datetime = datetime.today()
    reason = SCHEDULED
    reason_missed = None
    info_source = 'subject'
