from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.sites import all_sites
from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_appointment.constants import COMPLETE_APPT
from edc_appointment.models import Appointment
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_sites.site import sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ...constants import CLOSED_TIMEPOINT, OPEN_TIMEPOINT
from ...model_mixins import UnableToCloseTimepoint
from ...timepoint import TimepointClosed
from ..models import CrfOne, CrfTwo, SubjectVisit
from ..visit_schedule import visit_schedule


@tag("timepoint")
@override_settings(SITE_ID=10, SUBJECT_VISIT_MODEL="edc_timepoint.subjectvisit")
class TimepointTests(TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        sites._registry = {}
        sites.loaded = False
        sites.register(*all_sites)
        add_or_update_django_sites()

        return super().setUpClass()

    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)

        site_visit_schedules._registry = {}
        self.schedule = visit_schedule.schedules.get("schedule")
        site_visit_schedules.register(visit_schedule)
        helper = Helper(
            now=timezone.now() - relativedelta(years=1),
        )
        self.subject_visit = helper.enroll_to_baseline(
            visit_schedule_name=visit_schedule.name,
            schedule_name="schedule",
            subject_visit_model_cls=SubjectVisit,
        )
        self.subject_identifier = self.subject_visit.subject_identifier

        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")
        self.assertEqual(appointments.count(), 4)
        self.appointment = appointments[0]

    def create_crfs(self, visit_code: str):
        for crf in self.schedule.visits.get(visit_code).crfs:
            crf.model_cls.objects.create(subject_visit=self.subject_visit)

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
        """Assert timepoint does not close when tried."""
        self.assertEqual(self.appointment.timepoint_status, OPEN_TIMEPOINT)
        self.assertRaises(UnableToCloseTimepoint, self.appointment.timepoint_close_timepoint)

    def test_timepoint_status_closed_blocks_everything(self):
        """Assert timepoint closes because appointment status
        is "closed" and blocks further changes.
        """
        self.create_crfs(self.appointment.visit_code)
        self.appointment.appt_status = COMPLETE_APPT
        self.appointment.save()
        self.appointment.refresh_from_db()
        self.appointment.timepoint_close_timepoint()
        self.assertRaises(TimepointClosed, self.appointment.save)

    def test_timepoint_status_close_attempt_ok(self):
        """Assert timepoint closes because appointment status
        is "closed".
        """
        subject_visit = SubjectVisit.objects.get(
            appointment=self.appointment, reason=SCHEDULED
        )
        crf_obj = CrfOne.objects.create(subject_visit=subject_visit)
        CrfTwo.objects.create(subject_visit=subject_visit)
        self.appointment.appt_status = COMPLETE_APPT
        self.appointment.save()
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.appt_status, COMPLETE_APPT)
        self.appointment.timepoint_close_timepoint()
        self.assertRaises(TimepointClosed, self.appointment.save)
        self.assertRaises(TimepointClosed, subject_visit.save)
        self.assertRaises(TimepointClosed, crf_obj.save)

    def test_timepoint_status_attrs(self):
        """Assert timepoint closes because appointment status
        is COMPLETE_APPT and blocks further changes.
        """
        subject_visit = SubjectVisit.objects.get(
            appointment=self.appointment, reason=SCHEDULED
        )
        CrfOne.objects.create(subject_visit=subject_visit)
        CrfTwo.objects.create(subject_visit=subject_visit)
        self.appointment.appt_status = COMPLETE_APPT
        self.appointment.save()
        self.appointment.refresh_from_db()
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
        subject_visit = SubjectVisit.objects.get(
            appointment=self.appointment, reason=SCHEDULED
        )
        CrfOne.objects.create(subject_visit=subject_visit)
        crf_obj = CrfTwo.objects.create(subject_visit=subject_visit)
        self.appointment.appt_status = COMPLETE_APPT
        self.appointment.save()
        self.appointment.refresh_from_db()
        self.appointment.timepoint_close_timepoint()
        self.assertRaises(TimepointClosed, crf_obj.save)

    def test_timepoint_lookup_blocks_update(self):
        subject_visit = SubjectVisit.objects.get(
            appointment=self.appointment, reason=SCHEDULED
        )
        crf_obj = CrfOne.objects.create(subject_visit=subject_visit)
        CrfTwo.objects.create(subject_visit=subject_visit)
        self.appointment.appt_status = COMPLETE_APPT
        self.appointment.save()
        self.appointment.refresh_from_db()
        self.appointment.timepoint_close_timepoint()

        self.assertRaises(TimepointClosed, crf_obj.save)
        self.assertRaises(TimepointClosed, subject_visit.save)
