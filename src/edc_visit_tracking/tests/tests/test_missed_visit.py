from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings
from edc_appointment.constants import MISSED_APPT, ONTIME_APPT, SCHEDULED_APPT
from edc_appointment.exceptions import AppointmentBaselineError
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_constants.constants import (
    ALIVE,
    DEAD,
    HOSPITALIZED,
    NO,
    NOT_APPLICABLE,
    OTHER,
    YES,
)
from edc_facility.import_holidays import import_holidays
from edc_list_data import load_list_data
from edc_metadata.models import CrfMetadata
from edc_utils import get_utcnow
from edc_visit_schedule.constants import DAY1
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.visit import Crf, CrfCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED, UNSCHEDULED
from edc_visit_tracking.models import SubjectVisit, SubjectVisitMissedReasons
from visit_tracking_app.consents import consent_v1
from visit_tracking_app.models import list_data

from ..forms import SubjectVisitMissedForm
from ..helper import Helper

utc_tz = ZoneInfo("UTC")


@time_machine.travel(datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz))
class TestVisit(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        load_list_data(
            list_data=list_data,
            model_name="edc_visit_tracking.subjectvisitmissedreasons",
        )
        self.subject_identifier = "12345"
        site_consents.registry = {}
        site_consents.register(consent_v1)
        self.helper = self.helper_cls(subject_identifier=self.subject_identifier)
        crfs = CrfCollection(
            Crf(show_order=1, model="visit_tracking_app.crfone", required=True),
            Crf(show_order=2, model="visit_tracking_app.crftwo", required=True),
            Crf(show_order=3, model="visit_tracking_app.crfthree", required=True),
            Crf(show_order=4, model="visit_tracking_app.crffour", required=True),
            Crf(show_order=5, model="visit_tracking_app.crffive", required=True),
        )
        crfs_missed = CrfCollection(
            Crf(
                show_order=1,
                model="edc_visit_tracking.subjectvisitmissed",
                required=True,
            ),
        )

        visit_schedule1 = VisitSchedule(
            name="visit_schedule1",
            offstudy_model="visit_tracking_app.subjectoffstudy",
            death_report_model="visit_tracking_app.deathreport",
            locator_model="edc_locator.subjectlocator",
        )
        schedule1 = Schedule(
            name="schedule1",
            onschedule_model="visit_tracking_app.onscheduleone",
            offschedule_model="visit_tracking_app.offscheduleone",
            consent_definitions=[consent_v1],
        )
        visits = []
        for index in range(0, 4):
            visits.append(
                Visit(
                    code=f"{index + 1}000",
                    title=f"Day {index + 1}",
                    timepoint=index,
                    rbase=relativedelta(days=index),
                    rlower=relativedelta(days=0),
                    rupper=relativedelta(days=6),
                    requisitions=None,
                    crfs=crfs,
                    crfs_missed=crfs_missed,
                    allow_unscheduled=True,
                )
            )
        for visit in visits:
            schedule1.add_visit(visit)
        visit_schedule1.add_schedule(schedule1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)

    @staticmethod
    def get_subject_visit(
        visit_code=None,
        visit_code_sequence=None,
        appt_timing=None,
        visit_reason=None,
    ):
        appt_timing = appt_timing or ONTIME_APPT
        if visit_reason == MISSED_VISIT:
            appt_timing = MISSED_APPT
        visit_code = visit_code or DAY1
        visit_code_sequence = 0 if visit_code_sequence is None else visit_code_sequence
        if not visit_reason:
            if visit_code_sequence > 0:
                visit_reason = UNSCHEDULED
            else:
                visit_reason = MISSED_VISIT if appt_timing == MISSED_APPT else SCHEDULED_APPT
        appointment = Appointment.objects.get(
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
        )
        appointment.appt_timing = appt_timing
        appointment.save()
        opts = dict(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=visit_reason,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
        )
        try:
            subject_visit = SubjectVisit.objects.get(appointment=appointment)
        except ObjectDoesNotExist:
            subject_visit = SubjectVisit.objects.create(**opts)
        else:
            for k, v in opts.items():
                setattr(subject_visit, k, v)
            subject_visit.save()
            subject_visit.refresh_from_db()
        return appointment, subject_visit

    @override_settings(
        SUBJECT_MISSED_VISIT_REASONS_MODEL="edc_visit_tracking.subjectvisitmissed"
    )
    def test_(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        # baseline
        appointment, _ = self.get_subject_visit(appt_timing=ONTIME_APPT)
        appointment = appointment.next
        appointment.appt_timing = MISSED_APPT
        appointment.save()
        appointment.refresh_from_db()
        appointment, subject_visit = self.get_subject_visit(
            appt_timing=MISSED_APPT, visit_code=appointment.visit_code
        )
        opts = dict(
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            timepoint=appointment.timepoint,
        )
        self.assertGreater(CrfMetadata.objects.filter(**opts).count(), 0)
        subject_visit.reason = MISSED_VISIT
        subject_visit.save()
        self.assertEqual(1, CrfMetadata.objects.filter(**opts).count())

    @override_settings(
        SUBJECT_MISSED_VISIT_REASONS_MODEL="edc_visit_tracking.subjectvisitmissed"
    )
    def test_baseline_appt_can_never_be_missed(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        appointment.appt_timing = MISSED_APPT
        self.assertRaises(AppointmentBaselineError, appointment.save)

    @override_settings(
        SUBJECT_MISSED_VISIT_REASONS_MODEL="edc_visit_tracking.subjectvisitmissed"
    )
    def test_baseline_visit_can_never_be_missed(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        self.assertRaises(
            AppointmentBaselineError, self.get_subject_visit, visit_reason=MISSED_VISIT
        )

    @override_settings(
        SUBJECT_MISSED_VISIT_REASONS_MODEL="edc_visit_tracking.subjectvisitmissed"
    )
    def test_missed_appt_updates_subject_visit_as_missed(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        appointment, _ = self.get_subject_visit()
        appointment = appointment.next
        appointment.appt_timing = ONTIME_APPT
        appointment, subject_visit = self.get_subject_visit(
            visit_code=appointment.visit_code, visit_reason=SCHEDULED
        )
        self.assertEqual(subject_visit.reason, SCHEDULED)
        appointment.appt_timing = MISSED_APPT
        appointment.save()
        appointment.refresh_from_db()
        self.assertEqual(appointment.visit_code, "2000")
        subject_visit.refresh_from_db()
        self.assertEqual(subject_visit.reason, MISSED_VISIT)
        self.assertEqual(subject_visit.visit_code, "2000")

    @override_settings(
        SUBJECT_MISSED_VISIT_REASONS_MODEL="edc_visit_tracking.subjectvisitmissed"
    )
    def test_missed_appt_updates_subject_visit_as_missed2(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
            report_datetime=get_utcnow() - relativedelta(months=6),
        )
        appointment, _ = self.get_subject_visit()
        appointment = appointment.next
        appointment.appt_timing = MISSED_APPT
        appointment.save()
        appointment, subject_visit = self.get_subject_visit(
            visit_code=appointment.visit_code, visit_reason=MISSED_VISIT
        )
        data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            contact_last_date=subject_visit.report_datetime,
            survival_status=ALIVE,
            contact_attempted=YES,
            contact_made=YES,
            contact_attempts_count=3,
            missed_reasons=[SubjectVisitMissedReasons.objects.get(name=HOSPITALIZED)],
            ltfu=NO,
            site=Site.objects.get(id=settings.SITE_ID),
        )
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

        form.save(commit=True)

    def test_subject_visit_missed_form_survivial_and_ltfu(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        _, subject_visit = self.get_subject_visit()
        data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            survival_status=DEAD,
            contact_attempted=YES,
            contact_attempts_count=4,
            contact_attempts_explained=None,
            contact_last_date=get_utcnow(),
            missed_reasons=[SubjectVisitMissedReasons.objects.get(name=HOSPITALIZED)],
            contact_made=YES,
            ltfu=YES,
            site=Site.objects.get(id=settings.SITE_ID),
        )
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
        self.assertIn("ltfu", form._errors)

        data.update(survival_status=DEAD, ltfu=NOT_APPLICABLE)
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
        self.assertNotIn("ltfu", form._errors)

        data.update(survival_status=ALIVE, ltfu=NOT_APPLICABLE)
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
        self.assertIn("ltfu", form._errors)

    def test_subject_visit_missed_form_missed_reasons(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        _, subject_visit = self.get_subject_visit()
        data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            survival_status=ALIVE,
            contact_attempted=YES,
            contact_attempts_count=1,
            contact_last_date=get_utcnow(),
            missed_reasons=[SubjectVisitMissedReasons.objects.get(name=HOSPITALIZED)],
            contact_made=YES,
            ltfu=NO,
            site=Site.objects.get(id=settings.SITE_ID),
        )
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
        self.assertNotIn("missed_reasons_other", form._errors)
        data.update(missed_reasons=[SubjectVisitMissedReasons.objects.get(name=OTHER)])
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
        self.assertIn("missed_reasons_other", form._errors)

    def test_subject_visit_missed_form_attempts(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        _, subject_visit = self.get_subject_visit()
        data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            survival_status=ALIVE,
            contact_attempted=NO,
            contact_made=NOT_APPLICABLE,
            contact_attempts_count=None,
            missed_reasons=[SubjectVisitMissedReasons.objects.get(name=HOSPITALIZED)],
            ltfu=YES,
            site=Site.objects.get(id=settings.SITE_ID),
        )
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
        self.assertNotIn("contact_attempts_count", form._errors)

        data.update(contact_attempted=YES, contact_made=NO, contact_attempts_count=None)
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()

        self.assertIn("contact_attempts_count", form._errors)

        data.update(contact_attempted=YES, contact_made=NO, contact_attempts_count=2)
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
        self.assertIn("contact_attempts_explained", form._errors)

        data.update(contact_attempted=YES, contact_made=NO, contact_attempts_count=3)
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
        self.assertNotIn("contact_attempts_explained", form._errors)

    def test_baseline_subject_visit_cannot_be_missed(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        self.assertRaises(
            AppointmentBaselineError, self.get_subject_visit, visit_reason=MISSED_VISIT
        )

    def test_subject_visit_missed_form(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        _, subject_visit = self.get_subject_visit()
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[1]
        appointment.appt_timing = MISSED_APPT
        appointment.save()
        _, subject_visit = self.get_subject_visit(
            visit_code=appointment.visit_code,
            visit_code_sequence=appointment.visit_code_sequence,
            appt_timing=MISSED_APPT,
        )

        self.assertEqual(subject_visit.reason, MISSED_VISIT)
        self.assertEqual(subject_visit.appointment.appt_timing, MISSED_APPT)

        data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            survival_status=ALIVE,
            contact_attempted=NO,
            contact_made=NOT_APPLICABLE,
            contact_attempts_count=None,
            missed_reasons=[SubjectVisitMissedReasons.objects.get(name=HOSPITALIZED)],
            ltfu=YES,
            site=Site.objects.get(id=settings.SITE_ID),
        )
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
