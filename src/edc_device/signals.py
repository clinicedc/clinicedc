from django.apps import apps as django_apps
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

from . import device_permissions


def update_device_fields(instance):
    device_id = getattr(settings, "DEVICE_ID", None)
    app_config = django_apps.get_app_config("edc_device")
    if not instance.id:
        instance.device_created = device_id or app_config.device_id
    instance.device_modified = device_id or app_config.device_id


@receiver(pre_save, weak=False, dispatch_uid="check_device_on_pre_save")
def check_device_on_pre_save(sender, instance, raw, using, update_fields, **kwargs):
    """Updates device id."""
    if not raw:
        try:
            instance.device_created
            instance.device_modified
        except AttributeError:
            pass
        else:
            update_device_fields(instance)
            device_permissions.check(instance)
