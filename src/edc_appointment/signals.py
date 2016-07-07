from django.apps import apps as django_apps
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver


def appointment_model(self):
    return django_apps.get_app_config('edc_appointment').appointment_model


@receiver(post_save, sender=appointment_model)
@receiver(post_save, weak=False, dispatch_uid="appointment_post_save")
def appointment_post_save(sender, instance, raw, created, using, **kwargs):
    """Update the TimePointStatus in appointment if the field is empty."""
    if not raw:
        try:
            print("It has passed here")
            if not instance.time_point_status:
                if instance.appt_status == COMPLETE_APPT:
                    instance.time_point_status = CLOSED
                instance.save(update_fields=['time_point_status'])
        except AttributeError as e:
            if 'time_point_status' not in str(e):
                raise AttributeError(str(e))