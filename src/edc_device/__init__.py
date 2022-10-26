from importlib.metadata import version

__version__ = version("edc_device")

from .constants import CENTRAL_SERVER, CLIENT, MIDDLEMAN, NODE_SERVER
from .device_permission import (
    DeviceAddPermission,
    DeviceChangePermission,
    DevicePermissionAddError,
    DevicePermissionChangeError,
    DevicePermissions,
)

device_permissions = DevicePermissions()
