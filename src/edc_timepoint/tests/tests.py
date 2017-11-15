from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_appointment.constants import COMPLETE_APPT, NEW_APPT
from edc_appointment.models import Appointment

from ..constants import OPEN_TIMEPOINT, CLOSED_TIMEPOINT

from ..model_mixins import UnableToCloseTimepoint
from ..timepoint import TimepointClosed
from .models import CrfOne, SubjectVisit

app_config = django_apps.get_app_config('edc_timepoint')


class TimepointTests(TestCase):

    def setUp(self):
        """Note: by default edc_appointment.Appointment
        is a timepoint model.
        """
        self.subject_identifier = '12345'
        self.appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1000',
            appt_status=NEW_APPT)

    def test_timepoint_status_open_by_default(self):
        self.assertEqual(self.appointment.timepoint_status, OPEN_TIMEPOINT)

    def test_timepoint_status_open_date_equals_model_date(self):
        timepoint = app_config.timepoints.get(
            self.appointment._meta.label_lower)
        self.assertEqual(
            self.appointment.timepoint_opened_datetime,
            getattr(self.appointment, timepoint.datetime_field))

    def test_timepoint_status_close_attempt_fails1(self):
        """Assert timepoint does not closed when tried.
        """
        self.assertEqual(self.appointment.timepoint_status, OPEN_TIMEPOINT)
        self.assertRaises(
            UnableToCloseTimepoint,
            self.appointment.timepoint_close_timepoint)

    def test_timepoint_status_closed_blocks_everything(self):
        """Assert timepoint closes because appointment status
        is "closed" and blocks further changes.
        """
        self.appointment.appt_status = COMPLETE_APPT
        self.appointment.save()
        self.appointment.timepoint_close_timepoint()
        self.assertRaises(TimepointClosed, self.appointment.save)

    def test_timepoint_status_close_attempt_ok(self):
        """Assert timepoint closes because appointment status
        is "closed".
        """
        self.appointment.appt_status = COMPLETE_APPT
        self.appointment.save()
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment)
        crf_obj = CrfOne.objects.create(subject_visit=subject_visit)
        self.appointment.timepoint_close_timepoint()
        self.assertRaises(TimepointClosed, self.appointment.save)
        self.assertRaises(TimepointClosed, subject_visit.save)
        self.assertRaises(TimepointClosed, crf_obj.save)

    def test_timepoint_status_attrs(self):
        """Assert timepoint closes because appointment status
        is COMPLETE_APPT and blocks further changes.
        """
        self.appointment.delete()
        appointment = Appointment.objects.create(
            appt_datetime=get_utcnow() - relativedelta(days=10),
            visit_code='1000')
        appointment.appt_status = COMPLETE_APPT
        appointment.save()
        appointment.timepoint_close_timepoint()
        self.assertEqual(appointment.appt_status, COMPLETE_APPT)
        self.assertEqual(appointment.timepoint_opened_datetime,
                         appointment.appt_datetime)
        self.assertGreater(appointment.timepoint_closed_datetime,
                           appointment.timepoint_opened_datetime)
        self.assertEqual(appointment.timepoint_status, CLOSED_TIMEPOINT)

    @tag('2')
    def test_timepoint_lookup_blocks_crf_create(self):
        self.appointment.delete()
        appointment = Appointment.objects.create(
            appt_datetime=get_utcnow() - relativedelta(days=10),
            visit_code='1000',
            appt_status=COMPLETE_APPT)
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment)
        try:
            crf_obj = CrfOne.objects.create(subject_visit=subject_visit)
        except TimepointClosed:
            self.fail('TimepointError unexpectedly raised.')
        appointment.timepoint_close_timepoint()
        self.assertRaises(TimepointClosed, crf_obj.save)

    def test_timepoint_lookup_blocks_update(self):
        self.appointment.delete()
        appointment = Appointment.objects.create(
            appt_datetime=get_utcnow() - relativedelta(days=10))
        appointment.appt_status = COMPLETE_APPT
        appointment.save()
        subject_visit = SubjectVisit.objects.create(appointment=appointment)
        crf_model = CrfOne.objects.create(subject_visit=subject_visit)
        appointment.timepoint_close_timepoint()
        self.assertRaises(TimepointClosed, crf_model.save)
