from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from edc_auth import EVERYONE

from .models import UserProfile, Role
from .constants import CUSTOM_ROLE


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
                if CUSTOM_ROLE not in [obj.name for obj in instance.roles.all()]:
                    group_names = [
                        group.name for group in instance.user.groups.all()]
                    add_group_names = []
                    for role in instance.roles.all():
                        for group in role.groups.all():
                            if group.name not in group_names:
                                add_group_names.append(group.name)
                    add_group_names = list(set(add_group_names))
                    for name in add_group_names:
                        instance.user.groups.add(Group.objects.get(name=name))
            elif action == "post_remove":
                remove_group_names = []
                current_group_names = []
                for role in instance.roles.all():
                    current_group_names.extend(
                        [group.name for group in role.groups.all()])
                for role in Role.objects.filter(pk__in=pk_set):
                    remove_group_names.extend(
                        [group.name for group in role.groups.all()
                         if group.name not in current_group_names])
                for name in remove_group_names:
                    instance.user.groups.remove(Group.objects.get(name=name))
            user_group_names = [g.name for g in instance.user.groups.all()]
            if EVERYONE not in user_group_names:
                instance.user.groups.add(Group.objects.get(name=EVERYONE))
