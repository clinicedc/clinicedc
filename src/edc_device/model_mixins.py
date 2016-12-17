from django.apps import apps as django_apps
from django.db import models
from edc_device.exceptions import DevicePermissionError


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
        if self.id:
            if app_config.device_permissions.get(self._meta.label_lower):
                device_permission = app_config.device_permissions.get(self._meta.label_lower)
                if not device_permission.may_change(app_config.role):
                    raise DevicePermissionError(
                        'Device does not have permissions to change this model. Got role={}, model={}'.format(
                            app_config.role, self._meta.label_lower))
        if not self.id:
            self.device_created = app_config.device_id
        self.device_modified = app_config.device_id
        super().save(*args, **kwargs)

    def common_clean(self):
        app_config = django_apps.get_app_config('edc_device')
        if self.id:
            if app_config.device_permissions.get(self._meta.label_lower):
                device_permission = app_config.device_permissions.get(self._meta.label_lower)
                if not device_permission.may_change(app_config.role):
                    raise DevicePermissionError(
                        'Device does not have permissions to change this model. Got role={}, model={}'.format(
                            app_config.role, self._meta.label_lower))
        super().common_clean()

    class Meta:
        abstract = True
