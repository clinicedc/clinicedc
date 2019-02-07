from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from edc_visit_schedule import off_schedule_or_raise


@receiver(post_save, weak=False, dispatch_uid="create_appointments_on_post_save")
def create_appointments_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw and not kwargs.get("update_fields"):
        try:
            instance.create_appointments()
        except AttributeError as e:
            if "create_appointments" not in str(e):
                raise


@receiver(post_save, weak=False, dispatch_uid="appointment_post_save")
def appointment_post_save(sender, instance, raw, created, using, **kwargs):
    """Update the TimePointStatus in appointment if the
    field is empty.
    """
    if not raw:
        try:
            if not instance.time_point_status:
                instance.time_point_status
                instance.save(update_fields=["time_point_status"])
        except AttributeError as e:
            if "time_point_status" not in str(e):
                raise


@receiver(pre_delete, weak=False, dispatch_uid="appointments_on_pre_delete")
def appointments_on_pre_delete(sender, instance, using, **kwargs):
    try:
        opts = dict(
            subject_identifier=instance.subject_identifier,
            report_datetime=instance.appt_datetime,
            visit_schedule_name=instance.visit_schedule_name,
            schedule_name=instance.schedule_name,
        )
    except AttributeError:
        pass
    else:
        if instance.visit_code_sequence == 0:
            off_schedule_or_raise(**opts)
