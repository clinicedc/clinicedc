from django.apps import apps as django_apps
from django.db import models


class DeviceModelMixin(models.Model):
    """Mixin to add device created and modified fields and check device permissions."""

    device_created = models.CharField(
        max_length=10,
        blank=True)

    device_modified = models.CharField(
        max_length=10,
        blank=True)

    def save(self, *args, **kwargs):
        app_config = django_apps.get_app_config('edc_device')
        if not self.id:
            self.device_created = app_config.device_id
        try:
            device_permission = app_config.device_permissions.get(
                self._meta.label_lower)
            device_permission.check(self)
        except AttributeError:
            pass
        self.device_modified = app_config.device_id
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
