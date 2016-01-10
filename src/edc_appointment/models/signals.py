from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from edc_constants.constants import NEW_APPT, UNKEYED

from ..choices import APPT_STATUS

from .appointment import Appointment
from .pre_appointment_contact import PreAppointmentContact
from .subject_configuration import SubjectConfiguration
from .time_point_status import TimePointStatus


@receiver(post_save, weak=False, dispatch_uid="appointment_post_save")
def appointment_post_save(sender, instance, raw, created, using, **kwargs):
    """Creates the TimePointStatus instance if it does not already exist."""
    if not raw:
        try:
            if not instance.time_point_status:
                try:
                    instance.time_point_status = TimePointStatus.objects.get(
                        visit_code=instance.visit_definition.code,
                        subject_identifier=instance.registered_subject.subject_identifier)
                except TimePointStatus.DoesNotExist:
                    instance.time_point_status = TimePointStatus.objects.create(
                        visit_code=instance.visit_definition.code,
                        subject_identifier=instance.registered_subject.subject_identifier)
                instance.save(update_fields=['time_point_status'])
        except AttributeError as e:
            if 'time_point_status' not in str(e):
                raise AttributeError(str(e))


# @receiver(pre_delete, weak=False, dispatch_uid="appointment_pre_delete")
# def appointment_pre_delete(sender, instance, using, **kwargs):
#     """Deletes the TimePointStatus instance if it exists."""
#     if isinstance(instance, Appointment):
#         try:
#             TimePointStatus.objects.get(appointment=instance).delete()
#         except TimePointStatus.DoesNotExist:
#             pass


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


@receiver(post_save, weak=False, dispatch_uid="update_appointment_on_subject_configuration_post_save")
def update_appointment_on_subject_configuration_post_save(sender, instance, raw, created, using, **kwargs):
    """Updates \'NEW\' appointments for this subject_identifier to reflect this appt_status."""
    if not raw:
        if isinstance(instance, SubjectConfiguration):
            if NEW_APPT not in [x[0] for x in APPT_STATUS]:
                raise ImproperlyConfigured(
                    'SubjectConfiguration save() expects APPT_STATUS choices tuple '
                    'to have a \'{0}\' option. Not found. Got {1}'.format(NEW_APPT, APPT_STATUS))
            for appointment in Appointment.objects.filter(
                    registered_subject__subject_identifier=instance.subject_identifier, appt_status__iexact=UNKEYED):
                appointment.appt_type = instance.default_appt_type
                appointment.raw_save()
