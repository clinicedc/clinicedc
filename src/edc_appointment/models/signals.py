from django.db.models import get_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .appointment import Appointment
from .pre_appointment_contact import PreAppointmentContact


@receiver(post_save, weak=False, dispatch_uid="prepare_appointments_on_post_save")
def prepare_appointments_on_post_save(sender, instance, raw, created, using, **kwargs):
    """"""
    if not raw:
        try:
            instance.prepare_appointments(using)
        except AttributeError as e:
            if 'prepare_appointments' not in str(e):
                raise


@receiver(post_save, weak=False, dispatch_uid="pre_appointment_contact_on_post_save")
def pre_appointment_contact_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Counts number of attempts to contact and if confirmed and updated appointment.

    Once confirmed, the appointment instance remains flagged as confirmed."""
    if not raw:
        if isinstance(instance, PreAppointmentContact):
            # TODO: THIS LOGIC NEEDS to be review!!
            appointment_update_fields = []
            contact_count = PreAppointmentContact.objects.filter(
                appointment=instance.appointment).count()
            if instance.appointment.contact_count != contact_count:
                instance.appointment.contact_count = contact_count
                appointment_update_fields.append('contact_count')
            if instance.is_confirmed:
                # if not already confirmed in a previous or following instance, update
                if not PreAppointmentContact.objects.filter(
                        appointment=instance.appointment, is_confirmed=True).exclude(pk=instance.pk):
                    instance.appointment.is_confirmed = True
                elif not PreAppointmentContact.objects.filter(
                        appointment=instance.appointment, is_confirmed=True) and instance.appointment.is_confirmed:
                    instance.appointment.is_confirmed = False
                appointment_update_fields.append('is_confirmed')
            if appointment_update_fields:
                instance.appointment.save(using=using, update_fields=appointment_update_fields)


@receiver(post_delete, weak=False, dispatch_uid="pre_appointment_contact_on_post_delete")
def pre_appointment_contact_on_post_delete(sender, instance, using, **kwargs):
    """Calls post_delete method."""
    # TODO: THIS LOGIC NEEDS to be review!!
    if isinstance(instance, PreAppointmentContact):
        appointment_update_fields = []
        contact_count = PreAppointmentContact.objects.filter(appointment=instance.appointment).count()
        if instance.appointment.contact_count != contact_count:
            instance.appointment.contact_count = contact_count
            appointment_update_fields.append('contact_count')
        if instance.is_confirmed:
            # if not already confirmed in a previous or following instance, update
            if not PreAppointmentContact.objects.filter(
                    appointment=instance.appointment, is_confirmed=True).exclude(pk=instance.pk):
                instance.appointment.is_confirmed = True
            elif not PreAppointmentContact.objects.filter(
                    appointment=instance.appointment, is_confirmed=True) and instance.appointment.is_confirmed:
                instance.appointment.is_confirmed = False
            appointment_update_fields.append('is_confirmed')
        if appointment_update_fields:
            instance.appointment.save(using=using, update_fields=appointment_update_fields)


@receiver(post_save, weak=False, dispatch_uid="appointment_post_save")
def appointment_post_save(sender, instance, raw, created, using, **kwargs):
    """Creates the TimePointStatus instance if it does not already exist."""
    if not raw:
        if isinstance(instance, Appointment):
            TimePointStatus = get_model('data_manager', 'TimePointStatus')
            try:
                TimePointStatus.objects.get(appointment=instance)
            except TimePointStatus.DoesNotExist:
                TimePointStatus.objects.create(appointment=instance)
