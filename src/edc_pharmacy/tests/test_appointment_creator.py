from arrow import Arrow
from datetime import datetime
from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
from django.test import TestCase, tag
from edc_facility.facility import Facility
from edc_visit_schedule.visit.visit import Visit

from ..appointment_creator import AppointmentCreator
from unittest.case import skip


@skip('')
class TestAppointmentCreator(TestCase):

    def setUp(self):
        pass

    def test_(self):

        visit = Visit(code='1000', timepoint=0)
        facility = Facility(
            name='pharmacy',
            days=[MO, TU, WE, TH, FR, SA, SU])
        creator = AppointmentCreator(
            subject_identifier='12345',
            suggested_datetime=Arrow.fromdatetime(datetime(2017, 1, 1)),
            visit=visit,
            facility=facility,
            visit_schedule_name='pharmacy',
            schedule_name='pharmacy',
        )
        # print(creator.appointment)
        print(creator.appointment.appt_datetime)
