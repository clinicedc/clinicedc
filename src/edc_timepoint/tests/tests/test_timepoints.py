from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.test import TestCase
from edc_appointment.constants import COMPLETE_APPT
from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_appointment.models import Appointment
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ...constants import CLOSED_TIMEPOINT, OPEN_TIMEPOINT
from ...model_mixins import UnableToCloseTimepoint
from ...timepoint import TimepointClosed
from ..consents import v1
from ..models import CrfOne, CrfTwo, SubjectConsent, SubjectVisit
from ..visit_schedule import visit_schedule1


class Helper:
    def __init__(self, subject_identifier=None, now=None):
        self.subject_identifier = subject_identifier
        self.now = now or get_utcnow()

    def consent_and_put_on_schedule(self, subject_identifier=None):
        subject_identifier = subject_identifier or self.subject_identifier
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=subject_identifier,
            consent_datetime=self.now,
            identity="111111",
            confirm_identity="111111",
        )
        visit_schedule = site_visit_schedules.get_visit_schedule("visit_schedule1")
        schedule = visit_schedule.schedules.get("schedule1")
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        return subject_consent

    def add_unscheduled_appointment(self, appointment=None):
        creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            facility=appointment.facility,
            timepoint=appointment.timepoint + Decimal("0.1"),
        )
        return creator.appointment


class TimepointTests(TestCase):

    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        site_consents.register(v1)

        return super().setUpClass()

    def setUp(self):
        self.subject_identifier = "12345"
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=get_utcnow() - relativedelta(years=1),
        )
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")
        self.assertEqual(appointments.count(), 4)
        self.appointment = appointments[0]

    def test_timepoint_status_open_by_default(self):
        self.assertEqual(self.appointment.timepoint_status, OPEN_TIMEPOINT)

    def test_timepoint_status_open_date_equals_model_date(self):
        app_config = django_apps.get_app_config("edc_timepoint")
        timepoint = app_config.timepoints.get(self.appointment._meta.label_lower)
        self.assertEqual(
            self.appointment.timepoint_opened_datetime,
            getattr(self.appointment, timepoint.datetime_field),
        )

    def test_timepoint_status_close_attempt_fails1(self):
        """Assert timepoint does not closed when tried."""
        self.assertEqual(self.appointment.timepoint_status, OPEN_TIMEPOINT)
        self.assertRaises(UnableToCloseTimepoint, self.appointment.timepoint_close_timepoint)

    def test_timepoint_status_closed_blocks_everything(self):
        """Assert timepoint closes because appointment status
        is "closed" and blocks further changes.
        """
        subject_visit = SubjectVisit.objects.create(appointment=self.appointment)
        CrfOne.objects.create(subject_visit=subject_visit)
        CrfTwo.objects.create(subject_visit=subject_visit)
        self.appointment.appt_status = COMPLETE_APPT
        self.appointment.save()
        self.appointment.timepoint_close_timepoint()
        self.assertRaises(TimepointClosed, self.appointment.save)

    def test_timepoint_status_close_attempt_ok(self):
        """Assert timepoint closes because appointment status
        is "closed".
        """
        subject_visit = SubjectVisit.objects.create(appointment=self.appointment)
        crf_obj = CrfOne.objects.create(subject_visit=subject_visit)
        self.appointment.appt_status = COMPLETE_APPT
        self.appointment.save()
        self.appointment.refresh_from_db()
        self.appointment.timepoint_close_timepoint()
        self.assertRaises(TimepointClosed, self.appointment.save)
        self.assertRaises(TimepointClosed, subject_visit.save)
        self.assertRaises(TimepointClosed, crf_obj.save)

    def test_timepoint_status_attrs(self):
        """Assert timepoint closes because appointment status
        is COMPLETE_APPT and blocks further changes.
        """
        subject_visit = SubjectVisit.objects.create(appointment=self.appointment)
        CrfOne.objects.create(subject_visit=subject_visit)
        CrfTwo.objects.create(subject_visit=subject_visit)
        self.appointment.appt_status = COMPLETE_APPT
        self.appointment.save()
        self.appointment.timepoint_close_timepoint()
        self.assertEqual(self.appointment.appt_status, COMPLETE_APPT)
        self.assertEqual(
            self.appointment.timepoint_opened_datetime, self.appointment.appt_datetime
        )
        self.assertGreater(
            self.appointment.timepoint_closed_datetime,
            self.appointment.timepoint_opened_datetime,
        )
        self.assertEqual(self.appointment.timepoint_status, CLOSED_TIMEPOINT)

    def test_timepoint_lookup_blocks_crf_create(self):
        subject_visit = SubjectVisit.objects.create(appointment=self.appointment)
        self.appointment.appt_status = COMPLETE_APPT
        self.appointment.save()
        subject_visit = SubjectVisit.objects.get(pk=subject_visit.pk)
        try:
            crf_obj = CrfOne.objects.create(subject_visit=subject_visit)
        except TimepointClosed:
            self.fail("TimepointError unexpectedly raised.")
        self.appointment.timepoint_close_timepoint()
        self.assertRaises(TimepointClosed, crf_obj.save)

    def test_timepoint_lookup_blocks_update(self):
        subject_visit = SubjectVisit.objects.create(appointment=self.appointment)
        crf_obj = CrfOne.objects.create(subject_visit=subject_visit)
        self.appointment.appt_status = COMPLETE_APPT
        self.appointment.save()
        self.appointment.timepoint_close_timepoint()

        self.assertRaises(TimepointClosed, crf_obj.save)
        self.assertRaises(TimepointClosed, subject_visit.save)
