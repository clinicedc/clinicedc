from django.core.exceptions import ValidationError
from django.test import TestCase

from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from example.models import TestModel, Appointment
from example.visit_schedule import example_visit_schedule

from edc_constants.constants import CLOSED, COMPLETE_APPT, OPEN, IN_PROGRESS, NEW_APPT, INCOMPLETE, CANCELLED


class TestAppointmentMixin(TestCase):

    def setUp(self):
        site_visit_schedules.registry = {}
        site_visit_schedules.register(example_visit_schedule)
        TestModel.objects.create()
        self.appointments = Appointment.objects.all()

    def test_appointments_time_point_status_closed(self):
        """Test if appointment with status closed does not throw an error for time_poit_status closed."""
        appointment = self.appointments[0]
        appointment.appt_status = COMPLETE_APPT
        appointment.save(update_fields=['appt_status'])
        self.assertEqual(appointment.time_point_status, OPEN)
        appointment = Appointment.objects.get(pk=appointment.pk)
        if appointment.appt_status == COMPLETE_APPT:
            appointment.time_point_status = CLOSED
            appointment.save(update_fields=['time_point_status'])
        self.assertEqual(appointment.time_point_status, CLOSED)

    def test_edit_appointment_time_point_status_closed(self):
        """Test if an appointment with closed time point status throws an error."""
        appointment = self.appointments[0]
        appointment.appt_status = COMPLETE_APPT
        appointment.save(update_fields=['appt_status'])
        self.assertEqual(appointment.time_point_status, OPEN)
        # CLose time point status
        appointment = Appointment.objects.get(pk=appointment.pk)
        appointment.time_point_status = CLOSED
        appointment.save(update_fields=['time_point_status'])
        # Update appointment
        appointment = Appointment.objects.get(pk=appointment.pk)
        appointment.appt_status = IN_PROGRESS
        with self.assertRaisesMessage(
                ValidationError, 'Data entry for this time point is closed. See TimePointStatus.'):
            appointment.save(update_fields=['appt_status'])

    def test_appointment_close_time_point_status(self):
        """Test if an appointment with a status inprogess throws an error if is set to time point status is closed."""
        appointment = self.appointments[0]
        appointment.appt_status = IN_PROGRESS
        appointment.save(update_fields=['appt_status'])
        # CLose time point status
        appointment = Appointment.objects.get(pk=appointment.pk)
        appointment.time_point_status = CLOSED
        with self.assertRaisesMessage(ValidationError, 'Cannot close timepoint. Appointment status is IN_PROGRESS.'):
            appointment.save(update_fields=['time_point_status'])

    def test_appointment_close_time_point_status2(self):
        """Test if an appointment with a status new throws an error if is set to time point status is closed."""
        appointment = self.appointments[0]
        self.assertEqual(appointment.appt_status, NEW_APPT)
        # CLose time point status
        appointment = Appointment.objects.get(pk=appointment.pk)
        appointment.time_point_status = CLOSED
        with self.assertRaisesMessage(ValidationError, 'Cannot close timepoint. Appointment status is NEW.'):
            appointment.save(update_fields=['time_point_status'])

    def test_appointment_close_time_point_status3(self):
        """Test if an appointment with a status Incomplete does not throw an error if time point status is closed."""
        appointment = self.appointments[0]
        appointment.appt_status = INCOMPLETE
        appointment.save(update_fields=['appt_status'])
        self.assertEqual(appointment.appt_status, INCOMPLETE)
        # CLose time point status
        appointment = Appointment.objects.get(pk=appointment.pk)
        appointment.time_point_status = CLOSED
        self.assertEqual(appointment.time_point_status, CLOSED)

    def test_appointment_close_time_point_status4(self):
        """Test if an appointment with a status Cancelled does not throw an error if time point status is closed."""
        appointment = self.appointments[0]
        appointment.appt_status = CANCELLED
        appointment.save(update_fields=['appt_status'])
        self.assertEqual(appointment.appt_status, CANCELLED)
        # CLose time point status
        appointment = Appointment.objects.get(pk=appointment.pk)
        appointment.time_point_status = CLOSED
        self.assertEqual(appointment.time_point_status, CLOSED)
