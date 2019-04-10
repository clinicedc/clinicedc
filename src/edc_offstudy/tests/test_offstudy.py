from dateutil.relativedelta import relativedelta
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_appointment.tests.models import SubjectConsent, SubjectVisit
from edc_appointment.tests.models import SubjectOffstudy, OffScheduleOne
from edc_appointment.tests.visit_schedule import visit_schedule1, visit_schedule2
from edc_consent import NotConsentedError, site_consents
from edc_constants.constants import DEAD
from edc_facility.import_holidays import import_holidays
from edc_utils import get_utcnow, get_dob
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..utils import OffstudyError
from .consents import v1_consent
from .forms import SubjectOffstudyForm, CrfOneForm, NonCrfOneForm, BadNonCrfOneForm
from .models import BadNonCrfOne, CrfOne, NonCrfOne


class TestOffstudy(TestCase):
    @classmethod
    def setUpClass(cls):
        site_consents.register(v1_consent)
        import_holidays()
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.visit_schedule_name = "visit_schedule1"
        self.schedule_name = "schedule1"

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule1)
        site_visit_schedules.register(visit_schedule2)

        self.schedule1 = visit_schedule1.schedules.get("schedule1")
        self.schedule2 = visit_schedule2.schedules.get("schedule2")

        self.subject_identifier = "111111111"
        self.subject_identifiers = [
            self.subject_identifier,
            "222222222",
            "333333333",
            "444444444",
        ]
        self.consent_datetime = get_utcnow() - relativedelta(weeks=4)
        dob = get_dob(age_in_years=25, now=self.consent_datetime)
        for subject_identifier in self.subject_identifiers:
            subject_consent = SubjectConsent.objects.create(
                subject_identifier=subject_identifier,
                identity=subject_identifier,
                confirm_identity=subject_identifier,
                consent_datetime=self.consent_datetime,
                dob=dob,
            )
            self.schedule1.put_on_schedule(
                subject_identifier=subject_consent.subject_identifier,
                onschedule_datetime=self.consent_datetime,
            )
        self.subject_consent = SubjectConsent.objects.get(
            subject_identifier=self.subject_identifier, dob=dob
        )

    def test_offstudy_model(self):

        self.assertRaises(
            OffstudyError,
            SubjectOffstudy.objects.create,
            subject_identifier=self.subject_identifier,
            offstudy_datetime=(
                self.consent_datetime + relativedelta(days=1) + relativedelta(minutes=1)
            ),
        )

        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            offschedule_datetime=self.consent_datetime + relativedelta(days=1),
        )

        obj = SubjectOffstudy.objects.create(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=(
                self.consent_datetime + relativedelta(days=1) + relativedelta(minutes=1)
            ),
        )

        self.assertTrue(str(obj))

    def test_offstudy_cls_subject_not_registered_by_offstudy_date(self):

        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            offschedule_datetime=self.consent_datetime + relativedelta(days=1),
        )

        self.assertRaises(
            NotConsentedError,
            SubjectOffstudy.objects.create,
            subject_identifier=self.subject_identifier,
            offstudy_datetime=self.consent_datetime - relativedelta(days=1),
        )

    def test_update_subject_visit_report_date_after_offstudy_date(self):
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")
        appointment_datetimes = [
            appointment.appt_datetime for appointment in appointments
        ]
        # report visits for first and second appointment, 1, 2
        for index, appointment in enumerate(appointments[0:2]):
            SubjectVisit.objects.create(
                appointment=appointment,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                report_datetime=appointment_datetimes[index],
                study_status=SCHEDULED,
            )

        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            offschedule_datetime=appointment_datetimes[1],
        )

        # report off study on same date as second visit
        visit_schedule1.offstudy_model_cls.objects.create(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=appointment_datetimes[1],
            offstudy_reason=DEAD,
        )

        subject_visit = SubjectVisit.objects.all().order_by("report_datetime").last()
        subject_visit.report_datetime = subject_visit.report_datetime + relativedelta(
            years=1
        )
        self.assertRaises(OffstudyError, subject_visit.save)

    def test_crf_model_mixin(self):

        # get subject's appointments
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")

        # get first appointment
        # get first visit
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            visit_schedule_name=appointments[0].visit_schedule_name,
            schedule_name=appointments[0].schedule_name,
            visit_code=appointments[0].visit_code,
            report_datetime=appointments[0].appt_datetime,
            study_status=SCHEDULED,
        )
        # get crf_one for this visit
        crf_one = CrfOne(
            subject_visit=subject_visit, report_datetime=appointments[0].appt_datetime
        )
        crf_one.save()

        # get second appointment

        # create second visit
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[1],
            visit_schedule_name=appointments[1].visit_schedule_name,
            schedule_name=appointments[1].schedule_name,
            visit_code=appointments[1].visit_code,
            report_datetime=appointments[1].appt_datetime,
            study_status=SCHEDULED,
        )

        # take off schedule1
        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            offschedule_datetime=appointments[1].appt_datetime,
        )

        # create complete off-study form for 1 hour after
        # first visit date
        SubjectOffstudy.objects.create(
            offstudy_datetime=appointments[1].appt_datetime,
            subject_identifier=self.subject_identifier,
        )
        # show CRF saves OK
        crf_one = CrfOne(
            report_datetime=appointments[1].appt_datetime, subject_visit=subject_visit
        )
        try:
            crf_one.save()
        except OffstudyError as e:
            self.fail(f"OffstudyError unexpectedly raised. Got {e}")

        crf_one.report_datetime = crf_one.report_datetime + relativedelta(years=1)
        self.assertRaises(OffstudyError, crf_one.save)

    def test_non_crf_model_mixin(self):
        non_crf_one = NonCrfOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=self.consent_datetime,
        )

        # take off schedule1
        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            offschedule_datetime=(self.consent_datetime + relativedelta(hours=1)),
        )

        SubjectOffstudy.objects.create(
            offstudy_datetime=self.consent_datetime + relativedelta(hours=1),
            subject_identifier=self.subject_identifier,
        )
        try:
            non_crf_one.save()
        except OffstudyError as e:
            self.fail(f"OffstudyError unexpectedly raised. Got {e}")

        non_crf_one.report_datetime = non_crf_one.report_datetime + relativedelta(
            years=1
        )
        self.assertRaises(OffstudyError, non_crf_one.save)

    def test_bad_non_crf_model_mixin(self):
        self.assertRaises(
            ImproperlyConfigured,
            BadNonCrfOne.objects.create,
            subject_identifier=self.subject_identifier,
        )

    def test_modelform_mixin_ok(self):
        data = dict(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=get_utcnow(),
            offstudy_reason=DEAD,
        )
        # take off schedule1
        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            offschedule_datetime=(self.consent_datetime + relativedelta(hours=1)),
        )

        form = SubjectOffstudyForm(data=data)
        self.assertTrue(form.is_valid())

    def test_offstudy_modelform(self):
        data = dict(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=get_utcnow(),
            offstudy_reason=DEAD,
        )
        form = SubjectOffstudyForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Subject is on schedule on this date", str(form.errors))

        # take off schedule1
        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            offschedule_datetime=(self.consent_datetime + relativedelta(hours=1)),
        )

        form = SubjectOffstudyForm(data=data)
        self.assertTrue(form.is_valid())

    def test_crf_modelform_ok(self):
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")

        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            visit_schedule_name=appointments[0].visit_schedule_name,
            schedule_name=appointments[0].schedule_name,
            visit_code=appointments[0].visit_code,
            report_datetime=appointments[0].appt_datetime,
            study_status=SCHEDULED,
        )
        data = dict(
            subject_visit=str(subject_visit.id),
            report_datetime=appointments[0].appt_datetime,
        )
        form = CrfOneForm(data=data)
        self.assertTrue(form.is_valid())

        # take off schedule1
        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            offschedule_datetime=(
                appointments[0].appt_datetime + relativedelta(hours=1)
            ),
        )

        SubjectOffstudy.objects.create(
            offstudy_datetime=appointments[0].appt_datetime + relativedelta(hours=1),
            subject_identifier=self.subject_identifier,
        )
        form = CrfOneForm(data=data)
        self.assertTrue(form.is_valid())

        data = dict(
            subject_visit=str(subject_visit.id),
            report_datetime=appointments[0].appt_datetime + relativedelta(hours=2),
        )
        form = CrfOneForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Report date comes after subject", str(form.errors))

    def test_non_crf_modelform(self):

        data = dict(
            subject_identifier=self.subject_identifier,
            report_datetime=self.consent_datetime,
        )
        form = NonCrfOneForm(data=data)
        self.assertTrue(form.is_valid())

        # take off schedule1
        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            offschedule_datetime=(self.consent_datetime + relativedelta(hours=1)),
        )

        SubjectOffstudy.objects.create(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=(self.consent_datetime + relativedelta(hours=1)),
        )
        form = NonCrfOneForm(data=data)
        self.assertTrue(form.is_valid())

        data = dict(
            subject_identifier=self.subject_identifier,
            report_datetime=self.consent_datetime + relativedelta(hours=2),
        )
        form = NonCrfOneForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Report date comes after subject", str(form.errors))

    def test_bad_non_crf_modelform(self):
        data = dict(
            subject_identifier=self.subject_identifier,
            report_datetime=self.consent_datetime,
        )
        form = BadNonCrfOneForm(data=data)
        self.assertRaises(ImproperlyConfigured, form.is_valid)
