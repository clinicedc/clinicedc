from django.test import TestCase
from django.apps import apps as django_apps
from django.test.utils import override_settings

from ..constants import CENTRAL_SERVER, CLIENT, NODE_SERVER
from ..device_permission import DevicePermission
from ..device_permission import DevicePermissionAddError, DevicePermissionChangeError
from .models import TestModel


class TestDevicePermission(TestCase):

    def test_device_permission_app(self):
        device_permissions = {
            'edc_device.testmodel': DevicePermission(
                model='edc_device.testmodel',
                create_roles=[CENTRAL_SERVER],
                change_roles=[NODE_SERVER, CENTRAL_SERVER])
        }
        app_config = django_apps.get_app_config('edc_device')
        with override_settings(DEVICE_ID='10', DEVICE_ROLE=CLIENT):
            app_config.device_id = None
            app_config.device_permissions = device_permissions
            app_config.messages_written = False
            app_config.ready()

    def test_device_permission_add(self):
        device_permissions = {
            'edc_device.testmodel': DevicePermission(
                model='edc_device.testmodel',
                create_roles=[CENTRAL_SERVER],
                change_roles=[NODE_SERVER, CENTRAL_SERVER])
        }
        app_config = django_apps.get_app_config('edc_device')
        with override_settings(DEVICE_ID='10', DEVICE_ROLE=CLIENT):
            app_config.device_id = None
            app_config.device_permissions = device_permissions
            app_config.ready()
            self.assertRaises(
                DevicePermissionAddError,
                TestModel.objects.create)

    def test_device_permission_change(self):
        device_permissions = {
            'edc_device.testmodel': DevicePermission(
                model='edc_device.testmodel',
                create_roles=[CENTRAL_SERVER, CLIENT],
                change_roles=[NODE_SERVER, CENTRAL_SERVER])
        }
        app_config = django_apps.get_app_config('edc_device')
        with override_settings(DEVICE_ID='10', DEVICE_ROLE=CLIENT):
            app_config.device_id = None
            app_config.device_permissions = device_permissions
            app_config.ready()
            obj = TestModel.objects.create()
            self.assertRaises(DevicePermissionChangeError, obj.save)

    def test_device_permission_change_ok(self):
        device_permissions = {
            'edc_device.testmodel': DevicePermission(
                model='edc_device.testmodel',
                create_roles=[CENTRAL_SERVER, CLIENT],
                change_roles=[NODE_SERVER, CENTRAL_SERVER, CLIENT])
        }
        app_config = django_apps.get_app_config('edc_device')
        with override_settings(DEVICE_ID='10', DEVICE_ROLE=CLIENT):
            app_config.device_id = None
            app_config.device_permissions = device_permissions
            app_config.ready()
            obj = TestModel.objects.create()
            obj.save()
