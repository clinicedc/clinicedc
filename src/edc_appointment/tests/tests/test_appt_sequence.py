from django.db.models import ProtectedError
from django.db.models.signals import post_save
from django.test import TestCase
from edc_facility.import_holidays import import_holidays
from edc_protocol import Protocol
from edc_reference import site_reference_configs
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_appointment.managers import AppointmentDeleteError
from edc_appointment.models import Appointment
from edc_appointment.utils import delete_appointment_in_sequence, get_next_appointment
from edc_appointment_app.models import SubjectVisit
from edc_appointment_app.visit_schedule import visit_schedule1, visit_schedule2

from ..helper import Helper


class TestMoveAppointment(TestCase):
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
            now=Protocol().study_open_datetime,
        )
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_appointment_app.subjectvisit"}
        )
        self.helper.consent_and_put_on_schedule()
        appointments = Appointment.objects.filter(subject_identifier=self.subject_identifier)
        self.assertEqual(appointments.count(), 4)

        appointment = Appointment.objects.get(timepoint=0.0)
        SubjectVisit.objects.create(
            appointment=appointment,
            subject_identifier=appointment.subject_identifier,
            report_datetime=appointment.appt_datetime,
            visit_schedule_name=visit_schedule1.name,
            schedule_name="schedule1",
            visit_code="1000",
            reason=SCHEDULED,
        )
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save_base(update_fields=["appt_status"])
        appointment.refresh_from_db()

        for i in range(0, 3):
            creator = UnscheduledAppointmentCreator(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=visit_schedule1.name,
                schedule_name="schedule1",
                visit_code="1000",
                timepoint=appointment.timepoint,
                visit_code_sequence=appointment.visit_code_sequence + 1,
            )
            appointment = creator.appointment
            appointment.appt_status = INCOMPLETE_APPT
            appointment.save_base(update_fields=["appt_status"])

        self.appt_datetimes = [
            o.appt_datetime for o in Appointment.objects.all().order_by("appt_datetime")
        ]

    def test_resequence_appointments_correctly(self):
        def get_visit_codes():
            return [
                f"{o.visit_code}.{o.visit_code_sequence}"
                for o in Appointment.objects.all().order_by("appt_datetime")
            ]

        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "2000.0", "3000.0", "4000.0"],
            get_visit_codes(),
        )
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=1)
        appointment.delete()
        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "2000.0", "3000.0", "4000.0"],
            get_visit_codes(),
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
