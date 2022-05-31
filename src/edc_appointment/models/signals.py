from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from edc_utils import formatted_datetime, get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.model_mixins import VisitModelMixin

from ..appointment_status_updater import (
    AppointmentStatusUpdater,
    AppointmentStatusUpdaterError,
)
from ..constants import IN_PROGRESS_APPT
from ..managers import AppointmentDeleteError
from ..model_mixins import AppointmentModelMixin
from ..models import Appointment
from ..utils import (
    cancelled_appointment,
    get_appointment_model_name,
    missed_appointment,
    update_unscheduled_appointment_sequence,
)


@receiver(post_save, sender=Appointment, weak=False, dispatch_uid="appointment_post_save")
def appointment_post_save(sender, instance, raw, update_fields, **kwargs):
    if not raw:
        if not update_fields:
            # use the AppointmentStatusUpdater to set all
            # other appointments to be NOT in progress
            try:
                if instance.appt_status == IN_PROGRESS_APPT:
                    AppointmentStatusUpdater(instance, clear_others_in_progress=True)
            except AttributeError as e:
                if "appt_status" not in str(e):
                    raise
            except AppointmentStatusUpdaterError:
                pass
        # try to create_missed_visit_from_appointment
        # if appt_status == missed
        missed_appointment(instance)

        # try to delete subject visit
        # if appt status = CANCELLED_APPT
        cancelled_appointment(instance)


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


@receiver(post_save, weak=False, dispatch_uid="update_appt_status_on_subject_visit_post_save")
def update_appt_status_on_subject_visit_post_save(
    sender, instance, raw, update_fields, **kwargs
):
    if not raw and not update_fields:
        if isinstance(instance, (AppointmentModelMixin, VisitModelMixin)):
            try:
                AppointmentStatusUpdater(
                    instance.appointment,
                    change_to_in_progress=True,
                    clear_others_in_progress=True,
                )
            except AttributeError:
                pass
            except AppointmentStatusUpdaterError:
                pass


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
    else:
        # TODO: any conditions for unscheduled?
        pass


@receiver(
    post_delete, sender=Appointment, weak=False, dispatch_uid="appointments_on_post_delete"
)
def appointments_on_post_delete(sender, instance, using, **kwargs):
    # Holiday model comes in a sender, why ???
    if (
        not kwargs.get("update_fields")
        and sender._meta.label_lower == get_appointment_model_name()
    ):
        update_unscheduled_appointment_sequence(subject_identifier=instance.subject_identifier)
