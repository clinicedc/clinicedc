from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_action_item import site_action_items
from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_constants.constants import DEAD
from edc_facility.import_holidays import import_holidays
from edc_reference import site_reference_configs
from edc_utils import get_dob, get_utcnow
from edc_visit_schedule.exceptions import OffScheduleError
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

from edc_offstudy.models import SubjectOffstudy
from edc_offstudy.utils import OffstudyError

from ...action_items import EndOfStudyAction
from ..consents import v1_consent
from ..forms import CrfOneForm, NonCrfOneForm, SubjectOffstudyForm
from ..models import CrfOne, NonCrfOne, OffScheduleOne, SubjectConsent
from ..visit_schedule import visit_schedule1


class TestOffstudy(TestCase):
    @classmethod
    def setUpClass(cls):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule1)
        site_consents.register(v1_consent)
        import_holidays()
        site_action_items.register(EndOfStudyAction)
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

        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_visit_tracking.subjectvisit"}
        )
        self.schedule1 = visit_schedule1.schedules.get("schedule1")

        self.subject_identifier = "111111111"
        self.subject_identifiers = [
            self.subject_identifier,
            "222222222",
            "333333333",
            "444444444",
        ]

        self.consent_datetime = get_utcnow() - relativedelta(years=4)
        dob = get_dob(age_in_years=25, now=self.consent_datetime)
        for subject_identifier in self.subject_identifiers:
            subject_consent = SubjectConsent.objects.create(
                subject_identifier=subject_identifier,
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
            OffScheduleError,
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

    def test_offstudy_cls_raises_before_offstudy_date(self):
        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            offschedule_datetime=self.consent_datetime + relativedelta(days=1),
        )

        self.assertRaises(
            OffstudyError,
            SubjectOffstudy.objects.create,
            subject_identifier=self.subject_identifier,
            offstudy_datetime=self.consent_datetime - relativedelta(days=1),
        )

    def test_offstudy_not_before_offschedule(self):
        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            offschedule_datetime=self.consent_datetime + relativedelta(days=1),
        )

        self.assertRaises(
            OffstudyError,
            SubjectOffstudy.objects.create,
            subject_identifier=self.subject_identifier,
            offstudy_datetime=self.consent_datetime - relativedelta(days=1),
        )

    def test_update_subject_visit_report_date_after_offstudy_date(self):
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")
        appointment_datetimes = [appointment.appt_datetime for appointment in appointments]
        # report visits for first and second appointment, 1, 2
        for index, appointment in enumerate(appointments[0:2]):
            SubjectVisit.objects.create(
                appointment=appointment,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                visit_code_sequence=appointment.visit_code_sequence,
                report_datetime=appointment_datetimes[index],
                reason=SCHEDULED,
            )

        subject_visit = SubjectVisit.objects.all().order_by("report_datetime").last()

        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=subject_visit.report_datetime,
            offschedule_datetime=subject_visit.report_datetime,
        )

        # report off study on same date as second visit
        visit_schedule1.offstudy_model_cls.objects.create(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=appointment_datetimes[1],
            offstudy_reason=DEAD,
        )

        subject_visit = SubjectVisit.objects.all().order_by("report_datetime").last()
        subject_visit.report_datetime = subject_visit.report_datetime + relativedelta(years=1)
        self.assertRaises(OffstudyError, subject_visit.save)

    def test_crf_model_mixin(self):
        # get subject's appointments
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")

        # get first appointment
        # get first visit
        appointment = appointments[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )

        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()

        # get crf_one for this visit
        crf_one = CrfOne(
            subject_visit=subject_visit, report_datetime=appointment.appt_datetime
        )
        crf_one.save()

        # get second appointment

        # create second visit
        appointment = appointments[1]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()

        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")

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

    @override_settings(EDC_OFFSTUDY_OFFSTUDY_MODEL="edc_offstudy.SubjectOffstudy")
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

        non_crf_one.report_datetime = non_crf_one.report_datetime + relativedelta(years=1)
        self.assertRaises(OffstudyError, non_crf_one.save)

    @override_settings(EDC_OFFSTUDY_OFFSTUDY_MODEL="edc_offstudy.SubjectOffstudy")
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
        self.assertIn("Subject is still on a schedule", str(form.errors))

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
            reason=SCHEDULED,
        )
        data = dict(
            subject_visit=subject_visit,
            report_datetime=appointments[0].appt_datetime,
            visit_schedule_name=appointments[0].visit_schedule_name,
            schedule_name=appointments[0].schedule_name,
        )
        form = CrfOneForm(data=data)
        form.is_valid()

        self.assertEqual({}, form._errors)

        # take off schedule1
        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=appointments[0].appt_datetime,
            offschedule_datetime=appointments[0].appt_datetime + relativedelta(days=1),
        )

        SubjectOffstudy.objects.create(
            offstudy_datetime=appointments[0].appt_datetime + relativedelta(days=1),
            subject_identifier=self.subject_identifier,
        )
        form = CrfOneForm(data=data)
        self.assertTrue(form.is_valid())

        data = dict(
            subject_visit=subject_visit,
            report_datetime=appointments[0].appt_datetime + relativedelta(days=2),
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        form = CrfOneForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Subject not on schedule", str(form.errors))

    @override_settings(EDC_OFFSTUDY_OFFSTUDY_MODEL="edc_offstudy.SubjectOffstudy")
    def test_non_crf_modelform1(self):
        data = dict(
            subject_identifier=self.subject_identifier,
            report_datetime=self.consent_datetime,
        )
        form = NonCrfOneForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

    @override_settings(EDC_OFFSTUDY_OFFSTUDY_MODEL="edc_offstudy.SubjectOffstudy")
    def test_non_crf_modelform2(self):
        data = dict(
            subject_identifier=self.subject_identifier,
            report_datetime=self.consent_datetime,
        )

        # take off schedule1 and hour after trying to submit CRF
        OffScheduleOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            offschedule_datetime=(self.consent_datetime + relativedelta(hours=1)),
        )

        # take off study and hour after trying to submit CRF
        SubjectOffstudy.objects.create(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=(self.consent_datetime + relativedelta(hours=1)),
        )
        form = NonCrfOneForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
