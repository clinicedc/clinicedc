import contextlib
from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import CrfFour, SubjectConsent
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule_offstudy.visit_schedule import (
    get_visit_schedule,
)
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_action_item.site_action_items import AlreadyRegistered, site_action_items
from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_constants.constants import DEAD, INCOMPLETE
from edc_facility.import_holidays import import_holidays
from edc_offstudy.models import SubjectOffstudy
from edc_offstudy.utils import OffstudyError
from edc_sites.site import sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.exceptions import NotOnScheduleForDateError, OffScheduleError
from edc_visit_schedule.models import OffSchedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

from ...action_items import EndOfStudyAction
from ..forms import CrfFourForm, NonCrfOneForm, SubjectOffstudyForm
from ..models import NonCrfOne


@tag("offstudy")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC")))
class TestOffstudy(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        sites._registry = {}
        sites.loaded = False
        sites.register(*all_sites)
        add_or_update_django_sites()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        with contextlib.suppress(AlreadyRegistered):
            site_action_items.register(EndOfStudyAction)

    def setUp(self):
        helper = Helper()
        subject_visit = helper.enroll_to_baseline(
            visit_schedule_name="visit_schedule", schedule_name="schedule"
        )
        self.subject_identifier = subject_visit.subject_identifier
        for _ in range(0, 3):
            helper.enroll_to_baseline(
                visit_schedule_name="visit_schedule", schedule_name="schedule"
            )

        self.consent_datetime = SubjectConsent.objects.get(
            subject_identifier=self.subject_identifier
        ).consent_datetime

    def test_offstudy_model(self):
        traveller = time_machine.travel(
            self.consent_datetime + relativedelta(days=1) + relativedelta(minutes=1)
        )
        traveller.start()
        now = timezone.now()
        self.assertRaises(
            OffScheduleError,
            SubjectOffstudy.objects.create,
            subject_identifier=self.subject_identifier,
            offstudy_datetime=now,
        )

        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=timezone.now(),
            offschedule_datetime=now,
        )

        obj = SubjectOffstudy.objects.create(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=now,
        )

        self.assertTrue(str(obj))

    def test_offstudy_cls_raises_before_offstudy_date(self):
        traveller = time_machine.travel(self.consent_datetime + relativedelta(days=1))
        traveller.start()
        now = timezone.now()
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=timezone.now(),
            offschedule_datetime=now,
        )

        self.assertRaises(
            OffstudyError,
            SubjectOffstudy.objects.create,
            subject_identifier=self.subject_identifier,
            offstudy_datetime=now,
        )

    def test_offstudy_not_before_offschedule(self):
        traveller = time_machine.travel(self.consent_datetime + relativedelta(days=1))
        traveller.start()
        now = timezone.now()
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=now,
            offschedule_datetime=now,
        )

        self.assertRaises(
            OffstudyError,
            SubjectOffstudy.objects.create,
            subject_identifier=self.subject_identifier,
            offstudy_datetime=now - relativedelta(days=1),
        )

    def test_update_subject_visit_report_date_after_offstudy_date(self):
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier, visit_code="2000"
        )
        traveller = time_machine.travel(appointment.appt_datetime)
        traveller.start()
        now = timezone.now()
        SubjectVisit.objects.create(
            appointment=appointment,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            visit_code_sequence=appointment.visit_code_sequence,
            report_datetime=now,
            reason=SCHEDULED,
        )

        subject_visit = (
            SubjectVisit.objects.filter(subject_identifier=self.subject_identifier)
            .order_by("report_datetime")
            .last()
        )

        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=subject_visit.report_datetime,
            offschedule_datetime=subject_visit.report_datetime,
        )

        # report off study on same date as second visit
        SubjectOffstudy.objects.create(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=subject_visit.appointment.appt_datetime,
            offstudy_reason=DEAD,
        )
        traveller.stop()
        traveller = time_machine.travel(self.consent_datetime + relativedelta(years=1))
        traveller.start()
        now = timezone.now()
        subject_visit.report_datetime = now
        self.assertRaises(OffstudyError, subject_visit.save)

    def test_crf_model_mixin(self):
        # get subject's appointments
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")

        # get first appointment
        # get first visit
        appointment = appointments[0]
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()
        subject_visit = SubjectVisit.objects.get(appointment=appointment)

        # get crf_one for this visit
        crf = CrfFour(subject_visit=subject_visit, report_datetime=appointment.appt_datetime)
        crf.save()

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
        traveller = time_machine.travel(appointments[1].appt_datetime)
        traveller.start()
        now = timezone.now()
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=now,
            offschedule_datetime=now,
        )

        # create complete off-study form for 1 hour after
        # first visit date
        SubjectOffstudy.objects.create(
            offstudy_datetime=now,
            subject_identifier=self.subject_identifier,
        )
        # show CRF saves OK
        crf = CrfFour(report_datetime=now, subject_visit=subject_visit)
        try:
            crf.save()
        except OffstudyError as e:
            self.fail(f"OffstudyError unexpectedly raised. Got {e}")

        traveller.stop()
        traveller = time_machine.travel(self.consent_datetime + relativedelta(years=1))
        traveller.start()
        now = timezone.now()
        crf.report_datetime = now
        self.assertRaises(NotOnScheduleForDateError, crf.save)

    @override_settings(EDC_OFFSTUDY_OFFSTUDY_MODEL="edc_offstudy.SubjectOffstudy")
    def test_non_crf_model_mixin(self):
        traveller = time_machine.travel(self.consent_datetime + relativedelta(days=1))
        traveller.start()
        now = timezone.now()
        non_crf_one = NonCrfOne.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=self.consent_datetime,
        )

        # take off schedule1
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=now,
            offschedule_datetime=now,
        )

        SubjectOffstudy.objects.create(
            offstudy_datetime=now,
            subject_identifier=self.subject_identifier,
        )
        traveller.stop()
        traveller = time_machine.travel(self.consent_datetime + relativedelta(years=1))
        traveller.start()
        now = timezone.now()
        try:
            non_crf_one.save()
        except OffstudyError as e:
            self.fail(f"OffstudyError unexpectedly raised. Got {e}")

        non_crf_one.report_datetime = now
        self.assertRaises(OffstudyError, non_crf_one.save)

    @override_settings(EDC_OFFSTUDY_OFFSTUDY_MODEL="edc_offstudy.SubjectOffstudy")
    def test_modelform_mixin_ok(self):
        traveller = time_machine.travel(self.consent_datetime + relativedelta(days=1))
        traveller.start()
        now = timezone.now()
        data = dict(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=now,
            offstudy_reason=DEAD,
            site=Site.objects.get(id=settings.SITE_ID).id,
        )
        # take off schedule1
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=now,
            offschedule_datetime=now,
        )

        form = SubjectOffstudyForm(data=data)
        self.assertTrue(form.is_valid())

    def test_offstudy_modelform(self):
        traveller = time_machine.travel(self.consent_datetime + relativedelta(days=1))
        traveller.start()
        now = timezone.now()
        data = dict(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=now,
            offstudy_reason=DEAD,
            site=Site.objects.get(id=settings.SITE_ID).id,
        )
        form = SubjectOffstudyForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Subject is still on a schedule", str(form.errors))

        # take off schedule1
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=now,
            offschedule_datetime=now,
        )

        form = SubjectOffstudyForm(data=data)
        self.assertTrue(form.is_valid())

    @tag("offstudy7")
    def test_crf_modelform_ok(self):
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")

        subject_visit = SubjectVisit.objects.get(appointment=appointments[0])
        data = dict(
            subject_visit=subject_visit,
            report_datetime=appointments[0].appt_datetime,
            visit_schedule_name=appointments[0].visit_schedule_name,
            schedule_name=appointments[0].schedule_name,
            site=Site.objects.get(id=settings.SITE_ID).id,
            crf_status=INCOMPLETE,
        )
        form = CrfFourForm(data=data)
        form.is_valid()

        self.assertEqual({}, form._errors)

        traveller = time_machine.travel(appointments[0].appt_datetime + relativedelta(days=1))
        traveller.start()
        now = timezone.now()
        # take off schedule
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=now,
            offschedule_datetime=now,
        )

        SubjectOffstudy.objects.create(
            offstudy_datetime=now,
            subject_identifier=self.subject_identifier,
        )
        form = CrfFourForm(data=data)
        self.assertTrue(form.is_valid())

        traveller.stop()
        traveller = time_machine.travel(appointments[0].appt_datetime + relativedelta(days=4))
        traveller.start()
        now = timezone.now()
        data = dict(
            subject_visit=subject_visit,
            report_datetime=now,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            site=Site.objects.get(id=settings.SITE_ID).id,
            crf_status=INCOMPLETE,
        )
        form = CrfFourForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Subject not on schedule", str(form.errors))

    @override_settings(EDC_OFFSTUDY_OFFSTUDY_MODEL="edc_offstudy.SubjectOffstudy")
    def test_non_crf_modelform1(self):
        data = dict(
            subject_identifier=self.subject_identifier,
            report_datetime=self.consent_datetime,
            site=Site.objects.get(id=settings.SITE_ID).id,
        )
        form = NonCrfOneForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

    @override_settings(EDC_OFFSTUDY_OFFSTUDY_MODEL="edc_offstudy.SubjectOffstudy")
    def test_non_crf_modelform2(self):
        data = dict(
            subject_identifier=self.subject_identifier,
            report_datetime=self.consent_datetime,
            site=Site.objects.get(id=settings.SITE_ID).id,
        )

        traveller = time_machine.travel(self.consent_datetime + relativedelta(hours=1))
        traveller.start()
        now = timezone.now()
        # take off schedule1 and hour after trying to submit CRF
        OffSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=now,
            offschedule_datetime=now,
        )

        # take off study and hour after trying to submit CRF
        SubjectOffstudy.objects.create(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=now,
        )
        form = NonCrfOneForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
