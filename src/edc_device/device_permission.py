from django.apps import apps as django_apps
from django.core.exceptions import ValidationError


class DevicePermissionAddError(ValidationError):
    pass


class DevicePermissionChangeError(ValidationError):
    pass


class DevicePermissionError(Exception):
    pass


class BaseDevicePermission:
    label = None
    exception_cls = None
    device_roles = []
    device_ids = []

    def __init__(self, model=None, device_roles=None, device_ids=None):
        self.model = model
        self.device_roles = device_roles or self.device_roles
        self.device_ids = device_ids or self.device_ids

    def __repr__(self):
        return f"{self.__class__.__name__}({self.model},{self.device_roles})"

    def __str__(self):
        roles = ",".join(self.device_roles)
        return f"{self.model} {self.label} {roles}"

    def model_operation(self, model_obj=None, **kwargs):
        """Override."""
        raise DevicePermissionError("Method not implemented")

    @property
    def _permit_model_operation(self):
        app_config = django_apps.get_app_config("edc_device")
        if (
            app_config.device_role in self.device_roles
            or app_config.device_id in self.device_ids
        ):
            return True
        return False

    def check(self, model_obj=None, err_message=None, **kwargs):
        if not self.model:
            self.model = model_obj._meta.label_lower
        if model_obj._meta.label_lower == self.model:
            if (
                self.model_operation(model_obj=model_obj, **kwargs)
                and not self._permit_model_operation
            ):
                app_config = django_apps.get_app_config("edc_device")
                err_message = err_message or (
                    f"Device role may not {self.label.lower()} "
                    f"'{model_obj._meta.verbose_name}'."
                )
                raise self.exception_cls(
                    f"Device/Role has insufficient permissions for action. "
                    f"Got {err_message}. Device role is {app_config.device_role}.",
                    code=f"{self.label}_permission",
                )


class DeviceAddPermission(BaseDevicePermission):
    label = "ADD"
    exception_cls = DevicePermissionAddError

    def model_operation(self, model_obj=None, **kwargs):
        """Returns ADD if this is an add model."""
        if not model_obj.id:
            return self.label
        return None


class DeviceChangePermission(BaseDevicePermission):
    label = "CHANGE"
    exception_cls = DevicePermissionChangeError

    def model_operation(self, model_obj=None, **kwargs):
        """Returns CHANGE if this is a change model."""
        if model_obj.id:
            return self.label
        return None


class DevicePermissions:
    """Container class for registered device permission instances."""

    def __init__(self):  # , *device_permissions):
        self._registry = []
        self.n = 0
        self.models = []

    #         for device_permission in device_permissions:
    #             self.register(device_permission)

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        try:
            item = self._registry[self.n]
            self.n += 1
        except IndexError:
            raise StopIteration
        return item

    def reset(self):
        self._registry = []
        self.n = 0
        self.models = []

    def register(self, device_permission):
        self._registry.append(device_permission)
        self._registry = list(set(self._registry))
        if device_permission.model:
            self.models.append(device_permission.model)
            self.models = list(set(self.models))

    def check(self, model_obj=None, **kwargs):
        for device_permission in self._registry:
            device_permission.check(model_obj=model_obj, **kwargs)
