from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

import time_machine
from django.db.models import ProtectedError
from django.db.models.signals import post_save
from django.test import TestCase, override_settings
from edc_facility.import_holidays import import_holidays
from edc_metadata.models import CrfMetadata

from edc_appointment.constants import INCOMPLETE_APPT, NEW_APPT
from edc_appointment.managers import AppointmentDeleteError
from edc_appointment.models import Appointment
from edc_appointment.utils import delete_appointment_in_sequence, get_next_appointment
from edc_appointment_app.models import CrfOne, SubjectVisit
from edc_appointment_app.tests.appointment_app_test_case_mixin import (
    AppointmentAppTestCaseMixin,
)

from ..helper import Helper

utc_tz = ZoneInfo("UTC")


@override_settings(SITE_ID=10)
@time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz))
class TestMoveAppointment(AppointmentAppTestCaseMixin, TestCase):
    helper_cls = Helper

    def setUp(self):
        super().setUp()

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def test_appointments_resequence_after_delete(self):
        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(Appointment, order_by="appt_datetime"),
        )
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=1)
        appointment.delete()
        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(Appointment, order_by="appt_datetime"),
        )

    def test_resequence_appointment_correctly2(self):
        def get_visit_codes():
            return [
                f"{o.visit_code}.{o.visit_code_sequence}"
                for o in Appointment.objects.all().order_by("appt_datetime")
            ]

        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "2000.0", "3000.0", "4000.0"],
            get_visit_codes(),
        )
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=2)
        appointment.delete()
        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "2000.0", "3000.0", "4000.0"],
            get_visit_codes(),
        )

    def test_resequence_appointment_correctly3(self):
        def get_visit_codes():
            return [
                f"{o.visit_code}.{o.visit_code_sequence}"
                for o in Appointment.objects.all().order_by("appt_datetime")
            ]

        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "2000.0", "3000.0", "4000.0"],
            get_visit_codes(),
        )
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=3)
        appointment.delete()
        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "2000.0", "3000.0", "4000.0"],
            get_visit_codes(),
        )

    def test_delete_0_appointment_in_sequence(self):
        self.assertEqual(
            [0, 1, 2, 3],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=0)
        # raises ProtectedError because Subjectvisit exists
        self.assertRaises(ProtectedError, delete_appointment_in_sequence, appointment)
        SubjectVisit.objects.get(appointment=appointment).delete()
        # raises AppointmentDeleteError (from manager) because not allowed by manager
        self.assertRaises(AppointmentDeleteError, delete_appointment_in_sequence, appointment)
        # assert nothing was done
        self.assertEqual(
            [0, 1, 2, 3],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )

    def test_delete_first_appointment_in_sequence(self):
        post_save.disconnect(dispatch_uid="appointments_on_post_delete")
        self.assertEqual(
            [0, 1, 2, 3],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=1)
        delete_appointment_in_sequence(appointment)
        # update_unscheduled_appointment_sequence
        self.assertEqual(
            [0, 1, 2],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )

    def test_delete_second_appointment_in_sequence(self):
        self.assertEqual(
            [0, 1, 2, 3],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=2)
        delete_appointment_in_sequence(appointment)
        self.assertEqual(
            [0, 1, 2],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )

    def test_delete_third_appointment_in_sequence(self):
        self.assertEqual(
            [0, 1, 2, 3],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=3)
        delete_appointment_in_sequence(appointment)
        self.assertEqual(
            [0, 1, 2],
            [
                o.visit_code_sequence
                for o in Appointment.objects.filter(visit_code="1000").order_by(
                    "appt_datetime"
                )
            ],
        )

    def test_appointments_and_related_visits_resequence_after_appointment_is_deleted(self):
        for appointment in Appointment.objects.all().order_by("timepoint_datetime"):
            self.create_related_visit(appointment)
        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(Appointment, order_by="appt_datetime"),
        )
        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(SubjectVisit, order_by="report_datetime"),
        )
        appointment_10001 = Appointment.objects.get(visit_code="1000", visit_code_sequence=1)
        appointment_10001.related_visit.delete()
        appointment_10001.delete()
        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(Appointment, order_by="appt_datetime"),
        )
        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(SubjectVisit, order_by="report_datetime"),
        )

    def test_related_visit_resequences_after_appointment_is_deleted_with_crfs_submitted(
        self,
    ):
        for appointment in Appointment.objects.all().order_by("timepoint_datetime"):
            self.create_related_visit(appointment)
        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(Appointment, order_by="appt_datetime"),
        )
        # enter CRF on 1000.2
        appointment_10002 = Appointment.objects.get(visit_code="1000", visit_code_sequence=2)
        CrfOne.objects.create(subject_visit=appointment_10002.related_visit)
        CrfOne.objects.get(
            subject_visit__appointment__visit_code="1000",
            subject_visit__appointment__visit_code_sequence=2,
        )
        # delete 1000.1
        appointment_10001 = Appointment.objects.get(visit_code="1000", visit_code_sequence=1)
        appointment_10001.related_visit.delete()
        appointment_10001.delete()
        CrfOne.objects.get(
            subject_visit__appointment__visit_code="1000",
            subject_visit__appointment__visit_code_sequence=1,
        )

    def test_metadata_resequences_after_appointment_is_deleted(self):
        for appointment in Appointment.objects.all().order_by("timepoint_datetime"):
            self.create_related_visit(appointment)
        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(Appointment, order_by="appt_datetime"),
        )
        self.assertGreater(
            CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=1).count(), 0
        )
        self.assertGreater(
            CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=2).count(), 0
        )
        self.assertGreater(
            CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=3).count(), 0
        )
        # delete 1000.1
        appointment_10001 = Appointment.objects.get(visit_code="1000", visit_code_sequence=1)
        appointment_10001.related_visit.delete()
        appointment_10001.delete()

        self.assertGreater(
            CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=1).count(), 0
        )
        self.assertGreater(
            CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=2).count(), 0
        )
        self.assertEqual(
            CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=3).count(), 0
        )

    def test_appt_status_correct_after_appointment_is_deleted(self):
        for appointment in Appointment.objects.all().order_by("timepoint_datetime"):
            self.create_related_visit(appointment)
            appointment.refresh_from_db()
            self.assertEqual(appointment.appt_status, INCOMPLETE_APPT)

        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=3)
        appointment.related_visit.delete()
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=3)
        self.assertEqual(appointment.appt_status, NEW_APPT)

        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=1)
        appointment.related_visit.delete()
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=1)
        self.assertEqual(appointment.appt_status, NEW_APPT)

        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=1)
        self.assertEqual(appointment.appt_status, NEW_APPT)
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=2)
        self.assertEqual(appointment.appt_status, INCOMPLETE_APPT)
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=3)
        self.assertEqual(appointment.appt_status, NEW_APPT)

        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=1)
        appointment.delete()

        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=1)
        self.assertEqual(appointment.appt_status, INCOMPLETE_APPT)
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=2)
        self.assertEqual(appointment.appt_status, NEW_APPT)

    def test_next_getter(self):
        def get_visit_codes():
            return [
                f"{o.visit_code}.{o.visit_code_sequence}"
                for o in Appointment.objects.all().order_by("appt_datetime")
            ]

        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=0)

        self.assertEqual(appointment.visit_code, "1000")
        self.assertEqual(appointment.visit_code_sequence, 0)

        self.assertEqual(get_next_appointment(appointment).visit_code, "2000")
        self.assertEqual(get_next_appointment(appointment).visit_code_sequence, 0)
        self.assertEqual(
            get_next_appointment(appointment, include_interim=True).visit_code, "1000"
        )
        self.assertEqual(
            get_next_appointment(appointment, include_interim=True).visit_code_sequence, 1
        )
        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "2000.0", "3000.0", "4000.0"],
            get_visit_codes(),
        )
