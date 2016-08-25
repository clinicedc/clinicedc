from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, weak=False, dispatch_uid="create_appointments_on_post_save")
def create_appointments_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw and not kwargs.get('update_fields'):
        try:
            with transaction.atomic():
                instance.create_appointments()
        except AttributeError as e:
            if 'create_appointments' not in str(e):
                raise AttributeError(str(e))
