from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import time_machine
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase, override_settings
from edc_consent.site_consents import site_consents
from edc_constants.constants import INCOMPLETE
from edc_facility.import_holidays import import_holidays
from edc_protocol import Protocol
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED
from edc_visit_tracking.exceptions import RelatedVisitReasonError
from edc_visit_tracking.utils import get_related_visit_model_cls

from edc_appointment.constants import (
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    MISSED_APPT,
    ONTIME_APPT,
)
from edc_appointment.exceptions import AppointmentBaselineError
from edc_appointment.managers import AppointmentDeleteError
from edc_appointment.utils import get_appointment_model_cls
from edc_appointment_app.consents import v1_consent
from edc_appointment_app.models import OnScheduleOne, OnScheduleTwo, SubjectConsent
from edc_appointment_app.visit_schedule import get_visit_schedule1, get_visit_schedule2

from ..helper import Helper

if TYPE_CHECKING:
    from edc_visit_schedule.schedule import Schedule


utc_tz = ZoneInfo("UTC")


@override_settings(SITE_ID=10, EDC_SITES_REGISTER_DEFAULT=True)
@time_machine.travel(datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz))
class TestAppointment(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.subject_identifier = "12345"
        site_visit_schedules._registry = {}
        self.visit_schedule1 = get_visit_schedule1()
        self.schedule1: Schedule = self.visit_schedule1.schedules.get("schedule1")
        self.visit_schedule2 = get_visit_schedule2()
        site_visit_schedules.register(self.visit_schedule1)
        site_visit_schedules.register(self.visit_schedule2)
        site_consents.registry = {}
        site_consents.register(v1_consent)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=Protocol().study_open_datetime,
        )
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name, schedule_name=self.schedule1.name
        )

    def test_appointments_creation(self):
        """Assert appointment triggering method creates appointments."""
        appointments = get_appointment_model_cls().objects.filter(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(appointments.count(), 4)

    def test_appointments_creation2(self):
        """Asserts first appointment correctly selected if
        both visit_schedule_name and schedule_name provided.
        """
        OnScheduleTwo.objects.create(
            subject_identifier=self.subject_identifier, onschedule_datetime=get_utcnow()
        )
        self.assertEqual(get_appointment_model_cls().objects.all().count(), 8)

    def test_deletes_appointments(self):
        """Asserts manager method can delete appointments."""
        appointments = get_appointment_model_cls().objects.filter(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(appointments.count(), 4)

        get_related_visit_model_cls().objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )

        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=appointments[0].visit_schedule_name
        )
        schedule = visit_schedule.schedules.get(appointments[0].schedule_name)

        # this calls the manager method "delete_for_subject_after_date"
        schedule.offschedule_model_cls.objects.create(
            subject_identifier=self.subject_identifier,
            offschedule_datetime=appointments[0].appt_datetime,
        )

        self.assertEqual(
            get_appointment_model_cls()
            .objects.filter(subject_identifier=self.subject_identifier)
            .count(),
            1,
        )

    def test_deletes_appointments_with_unscheduled(self):
        """Asserts manager method can delete appointments."""
        appointments = get_appointment_model_cls().objects.filter(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(appointments.count(), 4)

        appointment = appointments[0]

        get_related_visit_model_cls().objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )

        appointment.refresh_from_db()
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()
        appointment.refresh_from_db()

        self.helper.add_unscheduled_appointment(appointment)
        self.assertEqual(appointments.count(), 5)

        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=appointment.visit_schedule_name
        )
        schedule = visit_schedule.schedules.get(appointment.schedule_name)

        # this calls the manager method "delete_for_subject_after_date"
        schedule.take_off_schedule(self.subject_identifier, appointment.appt_datetime)

        self.assertEqual(
            get_appointment_model_cls()
            .objects.filter(subject_identifier=self.subject_identifier)
            .count(),
            1,
        )

    def test_delete_single_appointment(self):
        appointments = get_appointment_model_cls().objects.filter(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(appointments.count(), 4)

        get_related_visit_model_cls().objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )

        appointment = appointments[0]
        appointment.refresh_from_db()
        self.assertEqual(appointment.appt_status, IN_PROGRESS_APPT)
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()
        appointment.refresh_from_db()
        self.assertEqual(appointment.appt_status, INCOMPLETE_APPT)

        # raised by Django
        with transaction.atomic():
            self.assertRaises(ProtectedError, appointment.delete)

        # raised in signal pre_delete
        with transaction.atomic():
            self.assertRaises(AppointmentDeleteError, appointments[1].delete)

        self.helper.add_unscheduled_appointment(appointment)
        self.assertEqual(appointments.count(), 5)

        unscheduled_appointment = get_appointment_model_cls().objects.get(
            visit_code="1000", visit_code_sequence=1
        )

        unscheduled_appointment.delete()
        self.assertEqual(appointments.count(), 4)

    def test_first_appointment_with_visit_schedule_and_schedule(self):
        """Asserts first appointment correctly selected if
        both visit_schedule_name and schedule_name provided.
        """
        subject_consent = SubjectConsent.objects.get(
            subject_identifier=self.subject_identifier
        )
        OnScheduleTwo.objects.create(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        onschedule_one = OnScheduleOne.objects.get(subject_identifier=self.subject_identifier)
        first_appointment = get_appointment_model_cls().objects.first_appointment(
            subject_identifier=onschedule_one.subject_identifier,
            visit_schedule_name=self.visit_schedule1,
            schedule_name=self.schedule1.name,
        )

        appointment = (
            get_appointment_model_cls()
            .objects.filter(
                subject_identifier=onschedule_one.subject_identifier,
                visit_schedule_name=self.visit_schedule1.name,
                schedule_name=self.schedule1.name,
            )
            .order_by("appt_datetime")[0]
        )

        self.assertEqual(first_appointment, appointment)

    def test_first_appointment_with_unscheduled(self):
        """Asserts first appointment correctly selected if
        unscheduled visits have been added.
        """
        subject_consent = SubjectConsent.objects.get(
            subject_identifier=self.subject_identifier
        )
        OnScheduleTwo.objects.create(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        onschedule_one = OnScheduleOne.objects.get(subject_identifier=self.subject_identifier)

        first_appointment = get_appointment_model_cls().objects.first_appointment(
            subject_identifier=onschedule_one.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )

        # add unscheduled
        get_related_visit_model_cls().objects.create(
            appointment=first_appointment,
            report_datetime=first_appointment.appt_datetime,
            reason=SCHEDULED,
        )
        first_appointment.appt_status = INCOMPLETE_APPT
        first_appointment.save()
        self.helper.add_unscheduled_appointment(first_appointment)

        appointment = (
            get_appointment_model_cls()
            .objects.filter(
                subject_identifier=onschedule_one.subject_identifier,
                visit_schedule_name=self.visit_schedule1.name,
                schedule_name=self.schedule1.name,
            )
            .order_by("appt_datetime")[0]
        )
        self.assertEqual(first_appointment, appointment)

    def test_next_appointment(self):
        onschedule = OnScheduleOne.objects.get(subject_identifier=self.subject_identifier)
        first_appointment = get_appointment_model_cls().objects.first_appointment(
            subject_identifier=onschedule.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )
        next_appointment = get_appointment_model_cls().objects.next_appointment(
            visit_code=first_appointment.visit_code,
            subject_identifier=onschedule.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )
        self.assertEqual(
            get_appointment_model_cls()
            .objects.filter(subject_identifier=onschedule.subject_identifier)
            .order_by("appt_datetime")[1],
            next_appointment,
        )

        next_appointment = get_appointment_model_cls().objects.next_appointment(
            appointment=first_appointment
        )
        self.assertEqual(
            get_appointment_model_cls()
            .objects.filter(subject_identifier=onschedule.subject_identifier)
            .order_by("appt_datetime")[1],
            next_appointment,
        )

    def test_next_appointment_with_unscheduled(self):
        onschedule = OnScheduleOne.objects.get(subject_identifier=self.subject_identifier)
        first_appointment = get_appointment_model_cls().objects.first_appointment(
            subject_identifier=onschedule.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )

        # add unscheduled
        get_related_visit_model_cls().objects.create(
            appointment=first_appointment,
            report_datetime=first_appointment.appt_datetime,
            reason=SCHEDULED,
        )
        first_appointment.appt_status = INCOMPLETE_APPT
        first_appointment.save()
        first_appointment.refresh_from_db()
        self.helper.add_unscheduled_appointment(first_appointment)

        next_appointment = get_appointment_model_cls().objects.next_appointment(
            visit_code=first_appointment.visit_code,
            subject_identifier=onschedule.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )
        self.assertEqual(
            get_appointment_model_cls()
            .objects.filter(
                subject_identifier=onschedule.subject_identifier, visit_code_sequence=0
            )
            .order_by("timepoint")[1],
            next_appointment,
        )

        next_appointment = get_appointment_model_cls().objects.next_appointment(
            appointment=first_appointment
        )
        self.assertEqual(
            get_appointment_model_cls()
            .objects.filter(
                subject_identifier=onschedule.subject_identifier, visit_code_sequence=0
            )
            .order_by("timepoint")[1],
            next_appointment,
        )

    def test_next_appointment_after_last_returns_none(self):
        """Assert returns None if next after last appointment."""

        last_appointment = get_appointment_model_cls().objects.last_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )
        self.assertEqual(
            get_appointment_model_cls().objects.next_appointment(appointment=last_appointment),
            None,
        )

    def test_next_appointment_after_last_returns_none_with_unscheduled(self):
        """Assert returns None if next after last appointment."""

        last_appointment = get_appointment_model_cls().objects.last_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )

        # add unscheduled
        for appointment in (
            get_appointment_model_cls()
            .objects.all()
            .order_by("timepoint", "visit_code_sequence")
        ):
            appointment.appt_status = IN_PROGRESS_APPT
            appointment.save()
            get_related_visit_model_cls().objects.create(
                appointment=appointment,
                report_datetime=appointment.appt_datetime,
                reason=SCHEDULED,
            )
            appointment.appt_status = INCOMPLETE_APPT
            appointment.save()
        self.helper.add_unscheduled_appointment(last_appointment)

        self.assertEqual(
            get_appointment_model_cls().objects.next_appointment(appointment=last_appointment),
            None,
        )

    def test_next_appointment_until_none(self):
        """Assert can walk from first to last appointment."""
        appointments = get_appointment_model_cls().objects.filter(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )
        first = get_appointment_model_cls().objects.first_appointment(
            appointment=appointments[0]
        )
        appts = [first]
        for appointment in appointments:
            appts.append(
                get_appointment_model_cls().objects.next_appointment(appointment=appointment)
            )
        self.assertIsNotNone(appts[0])
        self.assertEqual(appts[0], first)
        self.assertEqual(appts[-1], None)

    def test_previous_appointment1(self):
        """Assert returns None if relative to first appointment."""
        first_appointment = get_appointment_model_cls().objects.first_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )
        self.assertEqual(
            get_appointment_model_cls().objects.previous_appointment(
                appointment=first_appointment
            ),
            None,
        )

    def test_previous_appointment2(self):
        """Assert returns previous appointment."""
        first_appointment = get_appointment_model_cls().objects.first_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )
        next_appointment = get_appointment_model_cls().objects.next_appointment(
            appointment=first_appointment
        )
        self.assertEqual(
            get_appointment_model_cls().objects.previous_appointment(
                appointment=next_appointment
            ),
            first_appointment,
        )

    def test_next_and_previous_appointment3(self):
        """Assert accepts appointment or indiviual attrs."""
        first_appointment = get_appointment_model_cls().objects.first_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )
        next_appointment = get_appointment_model_cls().objects.next_appointment(
            visit_code=first_appointment.visit_code,
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule1.name,
            schedule_name=self.schedule1.name,
        )
        self.assertEqual(
            get_appointment_model_cls()
            .objects.filter(subject_identifier=self.subject_identifier)
            .order_by("appt_datetime")[1],
            next_appointment,
        )
        appointment = get_appointment_model_cls().objects.next_appointment(
            appointment=first_appointment
        )
        self.assertEqual(
            get_appointment_model_cls()
            .objects.filter(subject_identifier=self.subject_identifier)
            .order_by("appt_datetime")[1],
            appointment,
        )

    def test_raises_appt_timing_missed_at_baseline(self):
        appointments = (
            get_appointment_model_cls()
            .objects.filter(subject_identifier=self.subject_identifier)
            .order_by("timepoint")
        )
        self.assertEqual(appointments.count(), 4)
        appointment = appointments.first()
        appointment.appt_status = IN_PROGRESS_APPT
        appointment.appt_timing = MISSED_APPT
        self.assertRaises(AppointmentBaselineError, appointment.save)

    def test_appt_timing(self):
        appointments = (
            get_appointment_model_cls()
            .objects.filter(subject_identifier=self.subject_identifier)
            .order_by("timepoint")
        )
        self.assertEqual(appointments.count(), 4)
        # create report for baseline visit
        appointment = appointments.first()
        get_related_visit_model_cls().objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()

        # next appt
        appointment = appointment.next
        appointment.appt_timing = MISSED_APPT
        appointment.save()
        appointment.refresh_from_db()
        self.assertEqual(appointment.appt_timing, MISSED_APPT)

    def test_appointment_creates_subject_visit_if_missed(self):
        appointments = get_appointment_model_cls().objects.filter(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(appointments.count(), 4)
        # create report for baseline visit
        get_related_visit_model_cls().objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointment = get_appointment_model_cls().objects.get(id=appointments[1].id)
        appointment.appt_timing = MISSED_APPT
        appointment.save()
        appointment.refresh_from_db()
        try:
            subject_visit = get_related_visit_model_cls().objects.get(
                appointment__visit_code=appointment.visit_code
            )
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist unexpectedly raised")
        self.assertEqual(subject_visit.reason, MISSED_VISIT)
        self.assertIn("auto-created", subject_visit.comments)
        self.assertEqual(subject_visit.document_status, INCOMPLETE)

        # resave does not cause error
        appointment.save()

    def test_raises_if_subject_visit_reason_out_of_sync_with_appt(self):
        appointments = get_appointment_model_cls().objects.filter(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(appointments.count(), 4)
        # create report for baseline visit
        get_related_visit_model_cls().objects.create(
            appointment=appointments[0],
            report_datetime=appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        appointment = get_appointment_model_cls().objects.get(id=appointments[1].id)
        appointment.appt_timing = MISSED_APPT
        appointment.save()
        appointment.refresh_from_db()

        self.assertEqual(appointment.appt_status, IN_PROGRESS_APPT)

        # change subject visit to scheduled is ignored, forces
        # subject_visit.reason == MISSED_VISIT
        # you need to go to the appt
        self.assertEqual(appointment.appt_timing, MISSED_APPT)
        subject_visit = get_related_visit_model_cls().objects.get(
            appointment__visit_code=appointment.visit_code
        )
        subject_visit.reason = SCHEDULED
        self.assertRaises(RelatedVisitReasonError, subject_visit.save)

        subject_visit.refresh_from_db()
        self.assertEqual(subject_visit.reason, MISSED_VISIT)
        self.assertEqual(appointment.appt_timing, MISSED_APPT)

        # change appt to scheduled updates subject_visit
        appointment.appt_timing = ONTIME_APPT
        appointment.save()
        appointment.refresh_from_db()
        subject_visit.refresh_from_db()
        self.assertEqual(appointment.appt_timing, ONTIME_APPT)
        self.assertEqual(subject_visit.document_status, INCOMPLETE)
        self.assertEqual(subject_visit.reason, SCHEDULED)
