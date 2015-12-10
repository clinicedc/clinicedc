from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, weak=False, dispatch_uid="off_study_post_save")
def off_study_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        try:
            instance.delete_future_appointments_on_offstudy()
        except AttributeError as e:
            if 'delete_future_appointments_on_offstudy' not in str(e):
                raise AttributeError(str(e))
