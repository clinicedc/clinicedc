from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow
from edc_visit_schedule.exceptions import ScheduleError
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED

from edc_appointment.constants import (
    CANCELLED_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    NEW_APPT,
)
from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_appointment.exceptions import (
    CreateAppointmentError,
    InvalidParentAppointmentMissingVisitError,
    InvalidParentAppointmentStatusError,
    UnscheduledAppointmentNotAllowed,
)
from edc_appointment.models import Appointment
from edc_appointment_app.consents import consent_v1
from edc_appointment_app.models import SubjectVisit
from edc_appointment_app.visit_schedule import get_visit_schedule1, get_visit_schedule2

from ..helper import Helper

utc_tz = ZoneInfo("UTC")

N = NEW_APPT
INC = INCOMPLETE_APPT


def get_appointment(visit_code: str, visit_code_sequence: int, options=None):
    return Appointment.objects.get(
        subject_identifier=options.subject_identifier,
        visit_code=visit_code,
        visit_code_sequence=visit_code_sequence,
        visit_schedule_name=options.visit_schedule1.name,
        schedule_name=options.schedule1.name,
    )


def set_to_inprogress(obj: Appointment) -> Appointment:
    obj.appt_status = IN_PROGRESS_APPT
    obj.save()
    return Appointment.objects.get(id=obj.id)


def add_subject_visit(obj: Appointment) -> Appointment:
    SubjectVisit.objects.create(
        appointment=obj,
        subject_identifier=obj.subject_identifier,
        report_datetime=obj.appt_datetime,
        reason=SCHEDULED,
        visit_code=obj.visit_code,
        visit_code_sequence=obj.visit_code_sequence,
        visit_schedule_name=obj.visit_schedule_name,
        schedule_name=obj.schedule_name,
    )
    return Appointment.objects.get(id=obj.id)


def set_to_incomplete(obj: Appointment) -> Appointment:
    # close appt (set to INCOMPLETE_APPT)
    obj.appt_status = INCOMPLETE_APPT
    obj.save()
    return Appointment.objects.get(id=obj.id)


def appt_status() -> list[str]:
    return [obj.appt_status for obj in Appointment.objects.all().order_by("appt_datetime")]


def appt_status_detailed() -> list[tuple[str, int, str]]:
    return [
        (obj.visit_code, obj.visit_code_sequence, obj.appt_status)
        for obj in Appointment.objects.all().order_by("appt_datetime")
    ]


def get_unscheduled(obj: Appointment) -> Appointment:
    creator = UnscheduledAppointmentCreator(
        subject_identifier=obj.subject_identifier,
        visit_schedule_name=obj.visit_schedule_name,
        schedule_name=obj.schedule_name,
        visit_code=obj.visit_code,
        facility=obj.facility,
        suggested_visit_code_sequence=1,
    )
    return creator.appointment


@time_machine.travel(datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz))
@override_settings(SITE_ID=10)
class TestUnscheduledAppointmentCreator(SiteTestCaseMixin, TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.subject_identifier = "12345"
        self.visit_schedule1 = get_visit_schedule1()
        self.schedule1 = self.visit_schedule1.schedules.get("schedule1")
        self.visit_schedule2 = get_visit_schedule2()
        self.schedule2 = self.visit_schedule2.schedules.get("schedule2")
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule1)
        site_visit_schedules.register(self.visit_schedule2)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=datetime(2017, 1, 7, tzinfo=ZoneInfo("UTC")),
        )

    def test_unscheduled_allowed_but_raises_on_appt_status(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )
        visit = self.visit_schedule1.schedules.get(self.schedule1.name).visits.first
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
                    visit_schedule_name=self.visit_schedule1.name,
                    schedule_name=self.schedule1.name,
                    visit_code=visit.code,
                    suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
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
                    visit_schedule_name=self.visit_schedule1.name,
                    schedule_name=self.schedule1.name,
                    visit_code=visit.code,
                    suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
                )

    def test_unscheduled_not_allowed(self):
        self.assertRaises(
            UnscheduledAppointmentNotAllowed,
            UnscheduledAppointmentCreator,
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule2.name,
            schedule_name=self.schedule2.name,
            visit_code="5000",
            suggested_visit_code_sequence=1,
        )

    def test_appt_status(self):
        start_date = datetime(2017, 1, 7, tzinfo=ZoneInfo("UTC"))
        traveller = time_machine.travel(start_date)
        traveller.start()
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name, schedule_name=self.schedule1.name
        )
        traveller.stop()
        for visit in self.visit_schedule1.schedules.get(self.schedule1.name).visits.values():
            # with self.subTest(visit=visit):
            # get parent appointment
            new_appointment = None
            appointment = Appointment.objects.get(
                subject_identifier=self.subject_identifier,
                visit_code=visit.code,
                visit_code_sequence=0,
                timepoint=visit.timepoint,
                visit_schedule_name=self.visit_schedule1.name,
                schedule_name=self.schedule1.name,
            )
            traveller = time_machine.travel(appointment.appt_datetime)
            traveller.start()
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
                visit_schedule_name=self.visit_schedule1.name,
                schedule_name=self.schedule1.name,
            )
            appointment.refresh_from_db()
            self.assertTrue(appointment.related_visit, subject_visit)
            self.assertEqual(0, appointment.related_visit.visit_code_sequence)
            self.assertEqual(1, appointment.next_visit_code_sequence)

            # close appt (set to INCOMPLETE_APPT)
            appointment.appt_status = INCOMPLETE_APPT
            appointment.save()
            appointment.refresh_from_db()

            print(visit, appointment, appointment.related_visit, appointment.appt_status)

            traveller.stop()
            traveller = time_machine.travel(appointment.appt_datetime + relativedelta(days=1))
            traveller.start()

            # create unscheduled off of this appt
            creator = UnscheduledAppointmentCreator(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule1.name,
                schedule_name=self.schedule1.name,
                visit_code=visit.code,
                facility=appointment.facility,
                suggested_visit_code_sequence=1,
            )
            new_appointment = creator.appointment
            new_appointment.appt_status = IN_PROGRESS_APPT
            new_appointment.save()
            new_appointment.refresh_from_db()
            print(
                visit,
                new_appointment,
                new_appointment.related_visit,
                new_appointment.appt_status,
            )
            if new_appointment.appt_status != IN_PROGRESS_APPT:
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
            new_appointment.refresh_from_db()
            self.assertEqual(new_appointment.appt_status, INCOMPLETE_APPT)
            self.assertEqual(visit.timepoint, int(new_appointment.timepoint))
            traveller.stop()

    def test_appt_status2(self):

        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name, schedule_name=self.schedule1.name
        )

        # 1000
        self.assertEqual(appt_status(), [N, N, N, N])
        appointment = get_appointment("1000", 0, options=self)
        appointment = set_to_inprogress(appointment)
        self.assertEqual(appt_status(), [IN_PROGRESS_APPT, N, N, N])
        appointment = add_subject_visit(appointment)
        self.assertEqual(appt_status(), [IN_PROGRESS_APPT, N, N, N])
        appointment = set_to_incomplete(appointment)
        self.assertEqual(appt_status(), [INC, N, N, N])
        unscheduled_appointment = get_unscheduled(appointment)
        self.assertEqual(appt_status(), [INC, N, N, N, N])
        unscheduled_appointment = set_to_inprogress(unscheduled_appointment)
        self.assertEqual(appt_status(), [INC, IN_PROGRESS_APPT, N, N, N])
        unscheduled_appointment = add_subject_visit(unscheduled_appointment)
        self.assertEqual(appt_status(), [INC, IN_PROGRESS_APPT, N, N, N])
        set_to_incomplete(unscheduled_appointment)
        self.assertEqual(appt_status(), [INC, INC, N, N, N])

    def test_appt_status3(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name, schedule_name=self.schedule1.name
        )
        # 1000
        appointment = get_appointment("1000", 0, options=self)
        appointment = set_to_inprogress(appointment)
        appointment = add_subject_visit(appointment)
        appointment = set_to_incomplete(appointment)
        unscheduled_appointment = get_unscheduled(appointment)
        unscheduled_appointment = set_to_inprogress(unscheduled_appointment)
        unscheduled_appointment = add_subject_visit(unscheduled_appointment)
        set_to_incomplete(unscheduled_appointment)

        # 2000
        self.assertEqual(appt_status(), [INC, INC, N, N, N])
        appointment = get_appointment("2000", 0, options=self)
        appointment = set_to_inprogress(appointment)
        self.assertEqual(appt_status(), [INC, INC, IN_PROGRESS_APPT, N, N])
        appointment = add_subject_visit(appointment)
        self.assertEqual(appt_status(), [INC, INC, IN_PROGRESS_APPT, N, N])
        appointment = set_to_incomplete(appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, N, N])
        unscheduled_appointment = get_unscheduled(appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, N, N, N])
        unscheduled_appointment = set_to_inprogress(unscheduled_appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, IN_PROGRESS_APPT, N, N])
        unscheduled_appointment = add_subject_visit(unscheduled_appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, IN_PROGRESS_APPT, N, N])
        set_to_incomplete(unscheduled_appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, N, N])

    def test_appt_status4(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name, schedule_name=self.schedule1.name
        )
        for visit_code in ["1000", "2000"]:
            appointment = get_appointment(visit_code, 0, options=self)
            appointment = set_to_inprogress(appointment)
            appointment = add_subject_visit(appointment)
            appointment = set_to_incomplete(appointment)
            unscheduled_appointment = get_unscheduled(appointment)
            unscheduled_appointment = set_to_inprogress(unscheduled_appointment)
            unscheduled_appointment = add_subject_visit(unscheduled_appointment)
            set_to_incomplete(unscheduled_appointment)

        # 3000
        self.assertEqual(appt_status(), [INC, INC, INC, INC, N, N])
        appointment = get_appointment("3000", 0, options=self)
        appointment = set_to_inprogress(appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, IN_PROGRESS_APPT, N])
        appointment = add_subject_visit(appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, IN_PROGRESS_APPT, N])
        appointment = set_to_incomplete(appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, INC, N])
        unscheduled_appointment = get_unscheduled(appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, INC, N, N])
        unscheduled_appointment = set_to_inprogress(unscheduled_appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, INC, IN_PROGRESS_APPT, N])
        unscheduled_appointment = add_subject_visit(unscheduled_appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, INC, IN_PROGRESS_APPT, N])
        set_to_incomplete(unscheduled_appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, INC, INC, N])

    def test_appt_status5(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name, schedule_name=self.schedule1.name
        )
        for visit_code in ["1000", "2000", "3000"]:
            appointment = get_appointment(visit_code, 0, options=self)
            appointment = set_to_inprogress(appointment)
            appointment = add_subject_visit(appointment)
            appointment = set_to_incomplete(appointment)
            unscheduled_appointment = get_unscheduled(appointment)
            unscheduled_appointment = set_to_inprogress(unscheduled_appointment)
            unscheduled_appointment = add_subject_visit(unscheduled_appointment)
            set_to_incomplete(unscheduled_appointment)

        # 4000
        self.assertEqual(appt_status(), [INC, INC, INC, INC, INC, INC, N])
        appointment = get_appointment("4000", 0, options=self)
        appointment = set_to_inprogress(appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, INC, INC, IN_PROGRESS_APPT])
        appointment = add_subject_visit(appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, INC, INC, IN_PROGRESS_APPT])
        appointment = set_to_incomplete(appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, INC, INC, INC])
        unscheduled_appointment = get_unscheduled(appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, INC, INC, INC, N])
        unscheduled_appointment = set_to_inprogress(unscheduled_appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, INC, INC, INC, IN_PROGRESS_APPT])
        unscheduled_appointment = add_subject_visit(unscheduled_appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, INC, INC, INC, IN_PROGRESS_APPT])
        set_to_incomplete(unscheduled_appointment)
        self.assertEqual(appt_status(), [INC, INC, INC, INC, INC, INC, INC, INC])

    def test_unscheduled_timepoint_not_incremented(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name, schedule_name=self.schedule1.name
        )
        visit = self.visit_schedule1.schedules.get(self.schedule1.name).visits.first
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
                    suggested_visit_code_sequence=index,
                    facility=appointment.facility,
                )
                self.assertEqual(appointment.timepoint, creator.appointment.timepoint)
                self.assertNotEqual(
                    appointment.visit_code_sequence,
                    creator.appointment.visit_code_sequence,
                )
                self.assertEqual(
                    creator.appointment.visit_code_sequence,
                    appointment.visit_code_sequence + 1,
                )
                SubjectVisit.objects.create(
                    appointment=creator.appointment,
                    report_datetime=get_utcnow(),
                    reason=UNSCHEDULED,
                )
                creator.appointment.appt_status = INCOMPLETE_APPT
                creator.appointment.save()
                appointment = creator.appointment

    def test_appointment_title(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name, schedule_name=self.schedule1.name
        )
        appointment = Appointment.objects.first_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
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
            suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
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
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
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
            suggested_visit_code_sequence=next_appointment.visit_code_sequence + 1,
        )

        self.assertEqual(creator.appointment.title, "Day 2.1")

    def test_appointment_title_if_visit_schedule_changes(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name, schedule_name=self.schedule1.name
        )
        appointment = Appointment.objects.first_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
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
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )

        SubjectVisit.objects.create(
            appointment=next_appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        next_appointment.appt_status = INCOMPLETE_APPT
        next_appointment.visit_code = "1111"
        self.assertRaises(ScheduleError, next_appointment.save)

    def test_appt_datetime_is_after_calling_appointment(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )
        appointment = Appointment.objects.first_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )
        self.assertEqual(appointment.title, "Day 1")

        SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()

        # same date raises CreateAppointmentError
        self.assertRaises(
            CreateAppointmentError,
            UnscheduledAppointmentCreator,
            suggested_appt_datetime=appointment.appt_datetime,
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            facility=appointment.facility,
            suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
        )

        # earlier date raises CreateAppointmentError error
        self.assertRaises(
            CreateAppointmentError,
            UnscheduledAppointmentCreator,
            suggested_appt_datetime=appointment.appt_datetime - relativedelta(days=1),
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            facility=appointment.facility,
            suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
        )
