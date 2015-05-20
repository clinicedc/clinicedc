from datetime import datetime
from edc_appointment import Appointment, PreAppointmentContact
from edc_appointment import PreAppointmentContactFactory
from edc_appointment import BaseAppointmentTests


class PreAppointmentContactMethodTests(BaseAppointmentTests):

    def test_post_save(self):
        self.setup()
        appt_pk = self.appointment.pk
        # test edc_appointment defaults
        self.assertEqual(self.appointment.contact_count, 0)
        self.assertEqual(self.appointment.is_confirmed, False)
        # make an attempt to contact, but not confirmed
        # make an instance but do not "create", will update edc_appointment
        pre_appointment_contact = PreAppointmentContact(appointment=self.appointment, contact_datetime=datetime.today(), is_contacted='No', is_confirmed=False)
        self.assertEqual(pre_appointment_contact.post_save(), (0, False, False))
        self.assertEqual(self.appointment.contact_count, 0)
        self.assertEqual(self.appointment.is_confirmed, False)
        # make an instance but do not "create", will update edc_appointment
        pre_appointment_contact = PreAppointmentContact(appointment=self.appointment, contact_datetime=datetime.today(), is_contacted='Yes', is_confirmed=True)
        self.assertEqual(pre_appointment_contact.post_save(), (0, True, True))
        self.assertEqual(self.appointment.contact_count, 0)
        self.assertEqual(self.appointment.is_confirmed, True)
        # create an instance
        pre_appointment_contact = PreAppointmentContactFactory(appointment=self.appointment, is_confirmed=False)
        # check updated edc_appointment (contact_count, is_confirmed, dirty)
        # post save should do nothing (dirty=False)
        self.assertEqual(pre_appointment_contact.post_save(), (1, False, False))
        appointment = Appointment.objects.get(pk=appt_pk)
        # since pre-app was created, count is incremented
        self.assertEqual(appointment.contact_count, 1)
        # is _confirmed false because not instances of pre_appt exist except the current one
        self.assertEqual(appointment.is_confirmed, False)
 
        # make another attempt to contact,  but not confirmed
        pre_appointment_contact = PreAppointmentContactFactory(appointment=appointment, is_confirmed=False)
        self.assertEqual(pre_appointment_contact.post_save(), (2, False, False))
        # is _confirmed false because not instances of pre_appt exist except the current one and the one before, both have is_confirmed=False
        self.assertEqual(appointment.is_confirmed, False)
        # make another attempt to contact,  confirmed
        pre_appointment_contact = PreAppointmentContactFactory(
            appointment=appointment,
            is_confirmed=True)
        # even if you run post save again, it should update since self.pk is excluded
        self.assertEqual(pre_appointment_contact.post_save(), (3, True, True))
        self.assertEqual(appointment.contact_count, 3)
        self.assertEqual(appointment.is_confirmed, True)
        # requery DB for this edc_appointment
        appointment = Appointment.objects.get(pk=appt_pk)
        self.assertEqual(appointment.is_confirmed, True)
        self.assertEqual(appointment.contact_count, 3)
 
    def test_post_delete(self):
        """ post_delete() has to update edc_appointment contact_count and is_confirmed."""
        self.setup()
        PreAppointmentContactFactory(appointment=self.appointment, is_confirmed=False)
        pre_appointment_contact = PreAppointmentContactFactory(appointment=self.appointment)
        appointment = Appointment.objects.get(pk=self.appointment.pk)
        self.assertEqual(appointment.contact_count, 2)
        self.assertEqual(appointment.is_confirmed, True)
        pre_appointment_contact.delete()
        appointment = Appointment.objects.get(pk=self.appointment.pk)
        self.assertEqual(appointment.contact_count, 1)
        self.assertEqual(appointment.is_confirmed, False)
