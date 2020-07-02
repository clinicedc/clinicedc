from dateutil.relativedelta import relativedelta
from django.test import override_settings, TestCase, tag
from edc_appointment.models import Appointment
from edc_facility.import_holidays import import_holidays
from edc_metadata.models import CrfMetadata
from edc_reference import site_reference_configs
from edc_visit_schedule import Crf, FormsCollection, Schedule, Visit, VisitSchedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED

from ..helper import Helper
from ..models import SubjectVisit


class TestVisit(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
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

    @tag("1")
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
