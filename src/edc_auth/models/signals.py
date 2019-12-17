from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .user_profile import UserProfile


@receiver(
    post_save, weak=False, sender=User, dispatch_uid="update_user_profile_on_post_save"
)
def update_user_profile_on_post_save(sender, instance, raw, **kwargs):
    if not raw:
        try:
            instance.userprofile
        except ObjectDoesNotExist:
            UserProfile.objects.create(user=instance)


@receiver(
    m2m_changed, weak=False, dispatch_uid="update_user_groups_on_role_m2m_changed"
)
def update_user_groups_on_role_m2m_changed(sender, action, instance, pk_set, **kwargs):

    try:
        assert instance.roles.through == sender
    except (AttributeError, AssertionError):
        pass
    else:
        if action in ["post_add", "post_remove"]:
            if action == "post_add":
                instance.add_groups_for_roles(pk_set)
            elif action == "post_remove":
                instance.remove_groups_for_roles(pk_set)
