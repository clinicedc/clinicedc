from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from edc_utils import formatted_datetime, get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..managers import AppointmentDeleteError
from ..models import Appointment
from ..utils import cancelled_appointment, missed_appointment


@receiver(post_save, weak=False, dispatch_uid="create_appointments_on_post_save")
def create_appointments_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Method `Model.create_appointments` is not typically used.

    See schedule.put_on_schedule() in edc_visit_schedule.
    """
    if not raw and not kwargs.get("update_fields"):
        try:
            instance.create_appointments()
        except AttributeError as e:
            if "create_appointments" not in str(e):
                raise


@receiver(post_save, sender=Appointment, weak=False, dispatch_uid="appointment_post_save")
def appointment_post_save(sender, instance, raw, created, using, **kwargs):
    """Update the TimePointStatus in appointment if the
    field is empty.
    """
    if not raw:
        missed_appointment(instance)
        cancelled_appointment(instance)


@receiver(
    pre_delete, sender=Appointment, weak=False, dispatch_uid="appointments_on_pre_delete"
)
def appointments_on_pre_delete(sender, instance, using, **kwargs):
    if instance.visit_code_sequence == 0:
        schedule = site_visit_schedules.get_visit_schedule(
            instance.visit_schedule_name
        ).schedules.get(instance.schedule_name)
        onschedule_datetime = schedule.onschedule_model_cls.objects.get(
            subject_identifier=instance.subject_identifier
        ).onschedule_datetime
        try:
            offschedule_datetime = schedule.offschedule_model_cls.objects.get(
                subject_identifier=instance.subject_identifier
            ).offschedule_datetime
        except ObjectDoesNotExist:
            raise AppointmentDeleteError(
                f"Appointment may not be deleted. "
                f"Subject {instance.subject_identifier} is on schedule "
                f"'{instance.visit_schedule.verbose_name}.{instance.schedule_name}' "
                f"as of '{formatted_datetime(onschedule_datetime)}'. "
                f"Got appointment {instance.visit_code}.{instance.visit_code_sequence} "
                f"datetime {formatted_datetime(instance.appt_datetime)}. "
                f"Perhaps complete off schedule model "
                f"'{instance.schedule.offschedule_model_cls().verbose_name.title()}' "
                f"first."
            )
        else:
            if onschedule_datetime <= instance.appt_datetime <= offschedule_datetime:
                raise AppointmentDeleteError(
                    f"Appointment may not be deleted. "
                    f"Subject {instance.subject_identifier} is on schedule "
                    f"'{instance.visit_schedule.verbose_name}.{instance.schedule_name}' "
                    f"as of '{formatted_datetime(onschedule_datetime)}' "
                    f"until '{formatted_datetime(get_utcnow())}'. "
                    f"Got appointment datetime "
                    f"{formatted_datetime(instance.appt_datetime)}. "
                )
