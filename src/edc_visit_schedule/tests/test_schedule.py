from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_utils import get_utcnow

from ..schedule import Schedule, AlreadyRegisteredVisit
from ..schedule import ScheduleNameError
from ..visit import Visit
from .models import OnSchedule, OffSchedule


class TestSchedule(TestCase):
    def test_schedule_name(self):
        self.assertRaises(ScheduleNameError, Schedule, name="sched  ule")

    def test_visit_schedule_repr(self):
        """Asserts repr evaluates correctly.
        """
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            consent_model="edc_visit_schedule.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        self.assertTrue(schedule.__repr__())

    def test_visit_schedule_field_value(self):
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            consent_model="edc_visit_schedule.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        self.assertEqual(schedule.field_value, "schedule")

    def test_schedule_onschedule_model_is_none(self):
        self.assertRaises(
            AttributeError, Schedule, name="schedule", onschedule_model=None
        )

    def test_schedule_offschedule_model_is_none(self):
        self.assertRaises(
            AttributeError, Schedule, name="schedule", offschedule_model=None
        )

    def test_schedule_bad_label_lower(self):
        schedule = Schedule(
            name="schedule",
            onschedule_model="x.x",
            offschedule_model="edc_visit_schedule.offschedule",
            consent_model="edc_visit_schedule.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        errors = schedule.check()
        self.assertIsNotNone(errors)

    def test_schedule_bad_label_lower2(self):
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="x.x",
            consent_model="edc_visit_schedule.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        errors = schedule.check()
        self.assertIsNotNone(errors)

    def test_schedule_onschedule_model_cls(self):
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            consent_model="edc_visit_schedule.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        self.assertEqual(schedule.onschedule_model_cls, OnSchedule)

    def test_schedule_offschedule_model_cls(self):
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            consent_model="edc_visit_schedule.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        self.assertEqual(schedule.offschedule_model_cls, OffSchedule)

    def test_schedule_ok(self):
        Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            consent_model="edc_visit_schedule.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )

    def test_add_visits(self):
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            consent_model="edc_visit_schedule.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        for i in range(0, 5):
            visit = Visit(
                code=str(i),
                timepoint=i,
                rbase=relativedelta(days=i),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
            )
            try:
                schedule.add_visit(visit=visit)
            except AlreadyRegisteredVisit as e:
                self.fail(f"Exception unexpectedly raised. Got {e}")

    def test_add_visits_duplicate_code(self):
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            consent_model="edc_visit_schedule.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        visit = Visit(
            code=str(0),
            title="erik0",
            timepoint=0,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        schedule.add_visit(visit=visit)
        visit = Visit(
            code=str(0),
            title="erik1",
            timepoint=1,
            rbase=relativedelta(days=1),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        self.assertRaises(AlreadyRegisteredVisit, schedule.add_visit, visit=visit)

    def test_add_visits_duplicate_title(self):
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            consent_model="edc_visit_schedule.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        visit = Visit(
            code=str(0),
            title="erik",
            timepoint=0,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        schedule.add_visit(visit=visit)
        visit = Visit(
            code=str(1),
            title="erik",
            timepoint=1,
            rbase=relativedelta(days=1),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        self.assertRaises(AlreadyRegisteredVisit, schedule.add_visit, visit=visit)

    def test_add_visits_duplicate_timepoint(self):
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            consent_model="edc_visit_schedule.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        visit = Visit(
            code=str(0),
            timepoint=0,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        schedule.add_visit(visit=visit)
        visit = Visit(
            code=str(1),
            timepoint=0,
            rbase=relativedelta(days=1),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        self.assertRaises(AlreadyRegisteredVisit, schedule.add_visit, visit=visit)

    def test_add_visits_duplicate_rbase(self):
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            consent_model="edc_visit_schedule.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )
        visit = Visit(
            code=str(0),
            timepoint=0,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        schedule.add_visit(visit=visit)
        visit = Visit(
            code=str(1),
            timepoint=1,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        self.assertRaises(AlreadyRegisteredVisit, schedule.add_visit, visit=visit)


class TestScheduleWithVisits(TestCase):
    def setUp(self):
        self.schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            consent_model="edc_visit_schedule.subjectconsent",
            appointment_model="edc_appointment.appointment",
        )

    def test_order(self):
        for i in [3, 5, 1, 0, 2, 4]:
            visit = Visit(
                code=str(i),
                timepoint=i,
                rbase=relativedelta(days=i),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
            )
            self.schedule.add_visit(visit=visit)
        self.assertEqual(
            [v.timepoint for v in self.schedule.visits.values()], [0, 1, 2, 3, 4, 5]
        )

    def test_first_visit(self):
        for i in range(1, 5):
            visit = Visit(
                code=str(i),
                timepoint=i,
                rbase=relativedelta(days=i),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
            )
            self.schedule.add_visit(visit=visit)
        visit = Visit(
            code=str(0),
            timepoint=0,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        self.schedule.add_visit(visit=visit)
        self.assertEqual(self.schedule.visits.first, visit)

    def test_last_visit(self):
        for i in range(0, 5):
            visit = Visit(
                code=str(i),
                timepoint=i,
                rbase=relativedelta(days=i),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
            )
            self.schedule.add_visit(visit=visit)
        visit = Visit(
            code=str(6),
            timepoint=6,
            rbase=relativedelta(days=6),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
        )
        self.schedule.add_visit(visit=visit)
        self.assertEqual(self.schedule.visits.last, visit)

    def test_get_visit(self):
        for i in range(0, 5):
            visit = Visit(
                code=str(i),
                timepoint=i,
                rbase=relativedelta(days=i),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
            )
            self.schedule.add_visit(visit=visit)
        visit = self.schedule.visits.get("3")
        self.assertEqual(visit.code, "3")
        visit = self.schedule.visits.get("BLAH")
        self.assertIsNone(visit)

    def test_previous_visit(self):
        for i in range(0, 5):
            visit = Visit(
                code=str(i),
                timepoint=i,
                rbase=relativedelta(days=i),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
            )
            self.schedule.add_visit(visit=visit)
        visit = self.schedule.visits.previous("3")
        self.assertEqual(visit.code, "2")

    def test_next_visit(self):
        for i in range(0, 5):
            visit = Visit(
                code=str(i),
                timepoint=i,
                rbase=relativedelta(days=i),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
            )
            self.schedule.add_visit(visit=visit)
        visit = self.schedule.visits.next("3")
        self.assertEqual(visit.code, "4")

    def test_previous_visit_none(self):
        for i in range(0, 5):
            visit = Visit(
                code=str(i),
                timepoint=i,
                rbase=relativedelta(days=i),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
            )
            self.schedule.add_visit(visit=visit)
        self.assertIsNone(self.schedule.visits.previous("0"))

    def test_next_visit_none(self):
        for i in range(0, 5):
            visit = Visit(
                code=str(i),
                timepoint=i,
                rbase=relativedelta(days=i),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
            )
            self.schedule.add_visit(visit=visit)
        self.assertIsNone(self.schedule.visits.next("5"))

    def test_visit_dates(self):
        dt = get_utcnow()
        for index, seq in enumerate(range(0, 5)):
            visit = Visit(
                code=str(seq),
                timepoint=seq * (index + 1),
                rbase=relativedelta(days=seq * (index + 1)),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
            )
            self.schedule.add_visit(visit=visit)
        index = 0
        for k, v in self.schedule.visits.timepoint_dates(dt=dt).items():
            self.assertEqual(v - dt, timedelta(index * (index + 1)), msg=k)
            index += 1
