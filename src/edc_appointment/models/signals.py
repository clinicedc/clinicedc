from django.apps import apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from ..helpers import AppointmentHelper

from .appointment import Appointment
from .base_appointment_helper_model import BaseAppointmentHelperModel
from .base_appointment_mixin import BaseAppointmentMixin
from .base_registered_subject_model import BaseRegisteredSubjectModel
from .pre_appointment_contact import PreAppointmentContact


@receiver(post_save, weak=False, dispatch_uid="prepare_appointments_on_post_save")
def prepare_appointments_on_post_save(sender, instance, raw, created, using, **kwargs):
    """"""
    if not raw:
        if issubclass(sender, (BaseAppointmentHelperModel, BaseAppointmentMixin)):
            instance.prepare_appointments(using)


@receiver(post_delete, weak=False, dispatch_uid='delete_unused_appointments')
def delete_unused_appointments(sender, instance, **kwargs):
    """ Delete unused appointments linked to this instance on delete.

    This is an instance of a "membership" form """
    if isinstance(instance, BaseRegisteredSubjectModel):
        AppointmentHelper().delete_for_instance(instance)


@receiver(post_save, weak=False, dispatch_uid="pre_appointment_contact_on_post_save")
def pre_appointment_contact_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Counts number of attempts to contact and if confirmed and updated edc_appointment.

    Once confirmed, the edc_appointment instance remains flagged as confirmed."""
    if not raw:
        if isinstance(instance, PreAppointmentContact):
            # TODO: THIS LOGIC NEEDS to be review!!
            appointment_update_fields = []
            contact_count = PreAppointmentContact.objects.filter(appointment=instance.appointment).count()
            if instance.appointment.contact_count != contact_count:
                instance.appointment.contact_count = contact_count
                appointment_update_fields.append('contact_count')
            if instance.is_confirmed:
                # if not already confirmed in a previous or following instance, update
                if not PreAppointmentContact.objects.filter(appointment=instance.appointment, is_confirmed=True).exclude(pk=instance.pk):
                    instance.appointment.is_confirmed = True
                elif not PreAppointmentContact.objects.filter(appointment=instance.appointment, is_confirmed=True) and instance.appointment.is_confirmed:
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
            if not PreAppointmentContact.objects.filter(appointment=instance.appointment, is_confirmed=True).exclude(pk=instance.pk):
                instance.appointment.is_confirmed = True
            elif not PreAppointmentContact.objects.filter(appointment=instance.appointment, is_confirmed=True) and instance.appointment.is_confirmed:
                instance.appointment.is_confirmed = False
            appointment_update_fields.append('is_confirmed')
        if appointment_update_fields:
            instance.appointment.save(using=using, update_fields=appointment_update_fields)


@receiver(post_save, weak=False, dispatch_uid="appointment_post_save")
def appointment_post_save(sender, instance, raw, created, using, **kwargs):
    """Creates the TimePointStatus instance if it does not already exist."""
    if not raw:
        if isinstance(instance, Appointment):
            TimePointStatus = apps.get_model('data_manager', 'TimePointStatus')
            try:
                TimePointStatus.objects.get(appointment=instance)
            except TimePointStatus.DoesNotExist:
                TimePointStatus.objects.create(appointment=instance)
