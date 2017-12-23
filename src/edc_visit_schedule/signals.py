from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, weak=False, dispatch_uid='offschedule_model_on_post_save')
def offschedule_model_on_post_save(sender, instance, raw, created, **kwargs):
    if not raw:
        try:
            instance.take_off_schedule()
        except AttributeError:
            pass


@receiver(post_save, weak=False, dispatch_uid='onschedule_model_on_post_save')
def onschedule_model_on_post_save(sender, instance, raw, created, **kwargs):
    if not raw:
        try:
            instance.put_on_schedule()
        except AttributeError:
            pass
