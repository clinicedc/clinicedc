from django.test import TestCase, tag
from django.apps import apps as django_apps
from django.test.utils import override_settings

from ..constants import CENTRAL_SERVER, CLIENT, NODE_SERVER
from ..device_permission import DevicePermissions, DeviceAddPermission, DeviceChangePermission
from ..device_permission import DevicePermissionAddError, DevicePermissionChangeError
from .models import TestModel


class TestDevicePermission(TestCase):

    def setUp(self):
        self.device_permissions = DevicePermissions()

    def test_device_permissions_register(self):
        device_permission = DeviceAddPermission(
            model='edc_device.testmodel',
            device_roles=[CENTRAL_SERVER])
        self.device_permissions.register(device_permission)
        device_permission = DeviceChangePermission(
            model='edc_device.testmodel',
            device_roles=[NODE_SERVER, CENTRAL_SERVER])
        self.device_permissions.register(device_permission)

    def test_device_permission_app(self):
        device_permission = DeviceAddPermission(
            model='edc_device.testmodel',
            device_roles=[CENTRAL_SERVER])
        self.device_permissions.register(device_permission)
        device_permission = DeviceChangePermission(
            model='edc_device.testmodel',
            device_roles=[NODE_SERVER, CENTRAL_SERVER])
        self.device_permissions.register(device_permission)
        app_config = django_apps.get_app_config('edc_device')
        with override_settings(DEVICE_ID='10', DEVICE_ROLE=CLIENT):
            app_config.device_id = None
            app_config.device_permissions = self.device_permissions
            app_config.messages_written = False
            app_config.ready()

    @tag('1')
    def test_device_permission_add(self):
        device_permission = DeviceAddPermission(
            model='edc_device.testmodel',
            device_roles=[CENTRAL_SERVER])
        self.device_permissions.register(device_permission)
        device_permission = DeviceChangePermission(
            model='edc_device.testmodel',
            device_roles=[NODE_SERVER, CENTRAL_SERVER])
        self.device_permissions.register(device_permission)
        app_config = django_apps.get_app_config('edc_device')
        with override_settings(DEVICE_ID='10', DEVICE_ROLE=CLIENT):
            app_config.device_id = None
            app_config.device_permissions = self.device_permissions
            app_config.ready()
            self.assertRaises(
                DevicePermissionAddError,
                TestModel.objects.create)

    def test_device_permission_change(self):
        device_permission = DeviceAddPermission(
            model='edc_device.testmodel',
            device_roles=[CENTRAL_SERVER, CLIENT])
        self.device_permissions.register(device_permission)
        device_permission = DeviceChangePermission(
            model='edc_device.testmodel',
            device_roles=[NODE_SERVER, CENTRAL_SERVER])
        self.device_permissions.register(device_permission)
        app_config = django_apps.get_app_config('edc_device')
        with override_settings(DEVICE_ID='10', DEVICE_ROLE=CLIENT):
            app_config.device_id = None
            app_config.device_permissions = self.device_permissions
            app_config.ready()
            obj = TestModel.objects.create()
            self.assertRaises(DevicePermissionChangeError, obj.save)

    def test_device_permission_change_ok(self):
        device_permission = DeviceAddPermission(
            model='edc_device.testmodel',
            device_roles=[CENTRAL_SERVER, CLIENT])
        self.device_permissions.register(device_permission)
        device_permission = DeviceChangePermission(
            model='edc_device.testmodel',
            device_roles=[NODE_SERVER, CENTRAL_SERVER, CLIENT])
        self.device_permissions.register(device_permission)
        app_config = django_apps.get_app_config('edc_device')
        with override_settings(DEVICE_ID='10', DEVICE_ROLE=CLIENT):
            app_config.device_id = None
            app_config.device_permissions = self.device_permissions
            app_config.ready()
            obj = TestModel.objects.create()
            obj.save()
