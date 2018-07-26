from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, weak=False, sender=User,
          dispatch_uid='update_user_profile_on_post_save')
def update_user_profile_on_post_save(sender, instance, raw, **kwargs):
    if not raw:
        try:
            instance.userprofile
        except ObjectDoesNotExist:
            UserProfile.objects.create(user=instance)
