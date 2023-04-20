from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_facility.import_holidays import import_holidays
from edc_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule.schedule import ScheduleError
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED

from edc_appointment.constants import (
    CANCELLED_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    NEW_APPT,
)
from edc_appointment.creators import (
    InvalidParentAppointmentMissingVisitError,
    InvalidParentAppointmentStatusError,
    UnscheduledAppointmentCreator,
    UnscheduledAppointmentNotAllowed,
)
from edc_appointment.models import Appointment
from edc_appointment_app.models import SubjectVisit
from edc_appointment_app.visit_schedule import visit_schedule1, visit_schedule2

from ..helper import Helper


class TestUnscheduledAppointmentCreator(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        self.subject_identifier = "12345"
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=datetime(2017, 1, 7, tzinfo=ZoneInfo("UTC")),
        )

        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_appointment_app.subjectvisit"}
        )

    def test_unscheduled_allowed_but_raises_on_appt_status(self):
        self.helper.consent_and_put_on_schedule()
        schedule_name = "schedule1"
        visit = visit_schedule1.schedules.get(schedule_name).visits.first
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=visit.code,
            visit_code_sequence=0,
        )
        # subject_visit not created so expect exception because of
        # the missing subject_visit
        for appt_status in [NEW_APPT, IN_PROGRESS_APPT, CANCELLED_APPT]:
            with self.subTest(appt_status=appt_status):
                appointment.appt_status = appt_status
                appointment.save()
                self.assertEqual(appointment.appt_status, appt_status)
                self.assertRaises(
                    InvalidParentAppointmentMissingVisitError,
                    UnscheduledAppointmentCreator,
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=visit_schedule1.name,
                    schedule_name=schedule_name,
                    visit_code=visit.code,
                    visit_code_sequence=appointment.visit_code_sequence + 1,
                    timepoint=appointment.timepoint,
                )
        # add a subject_visit and expect exception to be raises because
        # of appt_status
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        appointment.refresh_from_db()
        self.assertEqual(appointment.related_visit, subject_visit)
        for appt_status in [NEW_APPT, INCOMPLETE_APPT, IN_PROGRESS_APPT, CANCELLED_APPT]:
            with self.subTest(appt_status=appt_status):
                appointment.appt_status = appt_status
                appointment.save()
                if appointment.appt_status == INCOMPLETE_APPT:
                    continue
                self.assertEqual(appointment.appt_status, appt_status)
                self.assertRaises(
                    InvalidParentAppointmentStatusError,
                    UnscheduledAppointmentCreator,
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=visit_schedule1.name,
                    schedule_name=schedule_name,
                    visit_code=visit.code,
                    visit_code_sequence=appointment.visit_code_sequence + 1,
                    timepoint=appointment.timepoint,
                )

    def test_unscheduled_not_allowed(self):
        self.assertRaises(
            UnscheduledAppointmentNotAllowed,
            UnscheduledAppointmentCreator,
            subject_identifier=self.subject_identifier,
            visit_schedule_name=visit_schedule2.name,
            schedule_name="schedule2",
            visit_code="5000",
            visit_code_sequence=1,
            timepoint=Decimal("5.0"),
        )

    def test_add_subject_visits(self):
        self.helper.consent_and_put_on_schedule()
        schedule_name = "schedule1"
        for visit in visit_schedule1.schedules.get(schedule_name).visits.values():
            with self.subTest(visit=visit):
                # get parent appointment
                appointment = Appointment.objects.get(
                    subject_identifier=self.subject_identifier,
                    visit_code=visit.code,
                    visit_code_sequence=0,
                    timepoint=visit.timepoint,
                    visit_schedule_name=visit_schedule1.name,
                    schedule_name=schedule_name,
                )
                appointment.appt_status = IN_PROGRESS_APPT
                appointment.save()
                appointment.refresh_from_db()

                # fill in subject visit report for this appointment
                subject_visit = SubjectVisit.objects.create(
                    appointment=appointment,
                    subject_identifier=self.subject_identifier,
                    report_datetime=appointment.appt_datetime,
                    reason=SCHEDULED,
                    visit_code=visit.code,
                    visit_code_sequence=0,
                    visit_schedule_name=visit_schedule1.name,
                    schedule_name=schedule_name,
                )
                appointment.refresh_from_db()
                self.assertTrue(appointment.related_visit, subject_visit)
                self.assertEqual(0, appointment.related_visit.visit_code_sequence)
                self.assertEqual(1, appointment.next_visit_code_sequence)

                # close appt (set to INCOMPLETE_APPT)
                appointment.appt_status = INCOMPLETE_APPT
                appointment.save()
                appointment.refresh_from_db()

                # create unscheduled off of this appt
                creator = UnscheduledAppointmentCreator(
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name=visit_schedule1.name,
                    schedule_name=schedule_name,
                    visit_code=visit.code,
                    facility=appointment.facility,
                    visit_code_sequence=appointment.visit_code_sequence + 1,
                    timepoint=appointment.timepoint,
                    appt_datetime=appointment.appt_datetime + relativedelta(days=1),
                )
                new_appointment = creator.appointment
                new_appointment.appt_status = IN_PROGRESS_APPT
                new_appointment.save()
                new_appointment.refresh_from_db()
                self.assertEqual(new_appointment.appt_status, IN_PROGRESS_APPT)

                # submit subject visit for the unscheduled appt
                subject_visit = SubjectVisit.objects.create(
                    appointment=new_appointment,
                    report_datetime=get_utcnow(),
                    reason=UNSCHEDULED,
                    visit_code=new_appointment.visit_code,
                    visit_code_sequence=new_appointment.visit_code_sequence,
                    visit_schedule_name=new_appointment.visit_schedule_name,
                    schedule_name=new_appointment.schedule_name,
                )
                self.assertEqual(1, new_appointment.visit_code_sequence)
                self.assertEqual(1, subject_visit.visit_code_sequence)

                # close the unscheduled appt (set to INCOMPLETE_APPT)
                new_appointment.appt_status = INCOMPLETE_APPT
                new_appointment.save()
                self.assertEqual(new_appointment.appt_status, INCOMPLETE_APPT)
                self.assertEqual(visit.timepoint, int(new_appointment.timepoint))

    def test_unscheduled_timepoint_not_incremented(self):
        self.helper.consent_and_put_on_schedule()
        schedule_name = "schedule1"
        visit = visit_schedule1.schedules.get(schedule_name).visits.first
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier, visit_code=visit.code
        )
        self.assertEqual(appointment.timepoint, Decimal("0.0"))
        SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()
        for index in range(1, 5):
            with self.subTest(index=index):
                creator = UnscheduledAppointmentCreator(
                    subject_identifier=appointment.subject_identifier,
                    visit_schedule_name=appointment.visit_schedule_name,
                    schedule_name=appointment.schedule_name,
                    visit_code=appointment.visit_code,
                    visit_code_sequence=appointment.visit_code_sequence + index,
                    facility=appointment.facility,
                    timepoint=appointment.timepoint,
                )
                self.assertEqual(appointment.timepoint, creator.appointment.timepoint)
                self.assertNotEqual(
                    appointment.visit_code_sequence,
                    creator.appointment.visit_code_sequence,
                )
                self.assertEqual(
                    creator.appointment.visit_code_sequence,
                    appointment.visit_code_sequence + index,
                )
                SubjectVisit.objects.create(
                    appointment=creator.appointment,
                    report_datetime=get_utcnow(),
                    reason=UNSCHEDULED,
                )
                creator.appointment.appt_status = INCOMPLETE_APPT
                creator.appointment.save()

    def test_appointment_title(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.first_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        self.assertEqual(appointment.title, "Day 1")

        SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()

        creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            facility=appointment.facility,
            visit_code_sequence=appointment.visit_code_sequence + 1,
            timepoint=appointment.timepoint,
        )
        self.assertEqual(creator.appointment.title, "Day 1.1")

        SubjectVisit.objects.create(
            appointment=creator.appointment, report_datetime=get_utcnow(), reason=UNSCHEDULED
        )
        creator.appointment.appt_status = INCOMPLETE_APPT
        creator.appointment.save()

        next_appointment = Appointment.objects.next_appointment(
            visit_code=appointment.visit_code,
            subject_identifier=self.subject_identifier,
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )

        SubjectVisit.objects.create(
            appointment=next_appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        next_appointment.appt_status = INCOMPLETE_APPT
        next_appointment.save()

        creator = UnscheduledAppointmentCreator(
            subject_identifier=next_appointment.subject_identifier,
            visit_schedule_name=next_appointment.visit_schedule_name,
            schedule_name=next_appointment.schedule_name,
            visit_code=next_appointment.visit_code,
            facility=next_appointment.facility,
            visit_code_sequence=next_appointment.visit_code_sequence + 1,
            timepoint=next_appointment.timepoint,
        )

        self.assertEqual(creator.appointment.title, "Day 2.1")

    def test_appointment_title_if_visit_schedule_changes(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.first_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )
        self.assertEqual(appointment.title, "Day 1")

        SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()

        next_appointment = Appointment.objects.next_appointment(
            visit_code=appointment.visit_code,
            subject_identifier=self.subject_identifier,
            visit_schedule_name="visit_schedule1",
            schedule_name="schedule1",
        )

        SubjectVisit.objects.create(
            appointment=next_appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        next_appointment.appt_status = INCOMPLETE_APPT
        next_appointment.visit_code = "1111"
        self.assertRaises(ScheduleError, next_appointment.save)
