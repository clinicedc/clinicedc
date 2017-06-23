from django.apps import apps as django_apps
from django.core.exceptions import ValidationError


class DevicePermissionAddError(ValidationError):
    pass


class DevicePermissionChangeError(ValidationError):
    pass


class DevicePermission:

    def __init__(self, model=None, create_roles=None, create_devices=None,
                 change_roles=None, change_devices=None):
        self.create_roles = create_roles or []
        self.create_devices = create_devices or []
        self.change_roles = change_roles or []
        self.change_devices = change_devices or []

    def may_add(self, value=None):
        add = False
        if value in self.create_roles + self.create_devices:
            add = True
        return add

    def may_change(self, value=None):
        change = False
        if value in self.change_roles + self.change_devices:
            change = True
        return change

    def is_add(self, model_obj=None, **kwargs):
        return not model_obj.id

    def is_change(self, model_obj=None, **kwargs):
        return model_obj.id

    def check(self, model_obj, **kwargs):
        app_config = django_apps.get_app_config('edc_device')
        if (self.is_add(model_obj=model_obj, **kwargs)
                and not self.may_add(app_config.device_role)):
            raise DevicePermissionAddError(
                f'Device does not have ADD permissions. '
                f'Got \'{app_config.device_role}\' may not add '
                f'\'{model_obj._meta.verbose_name}\'.',
                code='add_permissions')
        elif (self.is_change(model_obj, **kwargs)
              and not self.may_change(app_config.device_role)):
            raise DevicePermissionChangeError(
                f'Device does not have CHANGE permissions. '
                f'Got \'{app_config.device_role}\' may not change '
                f'\'{model_obj._meta.verbose_name}\'.',
                code='change_permissions')
