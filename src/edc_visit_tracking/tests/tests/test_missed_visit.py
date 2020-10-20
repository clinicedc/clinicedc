from dateutil.relativedelta import relativedelta
from django.test import override_settings, TestCase
from edc_appointment.models import Appointment
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
from edc_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule import Crf, FormsCollection, Schedule, Visit, VisitSchedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED

from ..forms import SubjectVisitMissedForm
from ..helper import Helper
from ..models import list_data, SubjectVisit, SubjectVisitMissedReasons


class TestVisit(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        load_list_data(
            list_data=list_data,
            model_name="edc_visit_tracking.subjectvisitmissedreasons",
        )
        self.subject_identifier = "12345"
        self.helper = self.helper_cls(subject_identifier=self.subject_identifier)
        crfs = FormsCollection(
            Crf(show_order=1, model="edc_metadata.crfone", required=True),
            Crf(show_order=2, model="edc_metadata.crftwo", required=True),
            Crf(show_order=3, model="edc_metadata.crfthree", required=True),
            Crf(show_order=4, model="edc_metadata.crffour", required=True),
            Crf(show_order=5, model="edc_metadata.crffive", required=True),
        )
        crfs_missed = FormsCollection(
            Crf(
                show_order=1,
                model="edc_visit_tracking.subjectvisitmissed",
                required=True,
            ),
        )

        visit_schedule1 = VisitSchedule(
            name="visit_schedule1",
            offstudy_model="edc_visit_tracking.subjectoffstudy",
            death_report_model="edc_visit_tracking.deathreport",
            locator_model="edc_locator.subjectlocator",
        )
        schedule1 = Schedule(
            name="schedule1",
            onschedule_model="edc_visit_tracking.onscheduleone",
            offschedule_model="edc_visit_tracking.offscheduleone",
            consent_model="edc_visit_tracking.subjectconsent",
            appointment_model="edc_appointment.appointment",
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
                    requisitions=[],
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
        site_reference_configs.register_from_visit_schedule(
            visit_models={
                "edc_appointment.appointment": "edc_visit_tracking.subjectvisit"
            }
        )

    @override_settings(
        SUBJECT_MISSED_VISIT_REASONS_MODEL="edc_visit_tracking.subjectvisitmissed"
    )
    def test_(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=SCHEDULED
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

    def test_subject_visit_missed_form(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[0]

        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=MISSED_VISIT
        )
        data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            survival_status=DEAD,
            contact_attempted=YES,
            contact_attempts_count=1,
            contact_last_date=get_utcnow(),
            missed_reasons=[SubjectVisitMissedReasons.objects.get(name=HOSPITALIZED)],
            contact_made=YES,
            ltfu=YES,
        )
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
        self.assertIn("ltfu", form._errors)
        self.assertNotIn("missed_reasons_other", form._errors)

        data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            survival_status=ALIVE,
            contact_attempted=NO,
            contact_attempts_count=1,
            contact_made=NOT_APPLICABLE,
            missed_reasons=[SubjectVisitMissedReasons.objects.get(name=HOSPITALIZED)],
            ltfu=YES,
        )
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
        self.assertIn("contact_attempts_count", form._errors)

        data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            survival_status=ALIVE,
            contact_attempted=NO,
            contact_attempts_count=None,
            contact_made=NOT_APPLICABLE,
            missed_reasons=[SubjectVisitMissedReasons.objects.get(name=HOSPITALIZED)],
            ltfu=YES,
        )
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
        self.assertIn("missed_reasons", form._errors)

        data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            survival_status=ALIVE,
            contact_attempted=YES,
            contact_attempts_count=1,
            contact_made=YES,
            contact_last_date=get_utcnow(),
            missed_reasons=[SubjectVisitMissedReasons.objects.get(name=OTHER)],
            ltfu=YES,
        )
        form = SubjectVisitMissedForm(data=data)
        form.is_valid()
        self.assertIn("missed_reasons_other", form._errors)
