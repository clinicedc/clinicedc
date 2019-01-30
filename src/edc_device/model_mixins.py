from django.apps import apps as django_apps
from django.db import models
from django.db.models import options

from .device_permission import DevicePermissions

if "device_permissions" not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("device_permissions",)


class DeviceModelMixin(models.Model):
    """Mixin to add device created and modified fields and
    check device permissions.
    """

    check_device_permissions = True

    device_created = models.CharField(max_length=10, blank=True)

    device_modified = models.CharField(max_length=10, blank=True)

    def save(self, *args, **kwargs):
        app_config = django_apps.get_app_config("edc_device")
        if not self.id:
            self.device_created = app_config.device_id
        self.device_modified = app_config.device_id
        if self.check_device_permissions:
            try:
                self._meta.device_permissions.check(self)
            except AttributeError:
                pass
            app_config.device_permissions.check(self)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        device_permissions = DevicePermissions()
