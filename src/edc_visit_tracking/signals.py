from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(
    post_save, weak=False, dispatch_uid="visit_tracking_check_in_progress_on_post_save"
)
def visit_tracking_check_in_progress_on_post_save(
    sender, instance, raw, created, using, **kwargs
):
    """Calls post_save method on the visit tracking instance.
    """
    if not raw:
        try:
            instance.post_save_check_appointment_in_progress()
        except AttributeError as e:
            if "post_save_check_appointment_in_progress" not in str(e):
                raise
