from django.apps import apps as django_apps
from django.test import TestCase
from django.test.client import RequestFactory
from django.views.generic.base import ContextMixin
from django.test.utils import override_settings

from ..constants import CLIENT
from ..view_mixins import EdcDeviceViewMixin
from ..views import HomeView
from django.contrib.auth.models import User


class TestView(EdcDeviceViewMixin, ContextMixin):
    pass


@override_settings(DEBUG=False, LIVE_SYSTEM=True)
class TestHomeView(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="erik")
        self.view = HomeView()
        self.view.request = RequestFactory()
        self.view.request.user = self.user
        self.view.request.META = {"HTTP_CLIENT_IP": "1.1.1.1"}

    def test_context(self):
        context = self.view.get_context_data()
        self.assertIn("project_name", context)
        self.assertIn("device_id", context)
        self.assertIn("device_role", context)
        self.assertIn("ip_address", context)


class TestViewMixin(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="erik")
        self.view = TestView()
        self.view.request = RequestFactory()
        self.view.request.user = self.user
        self.view.request.META = {"HTTP_CLIENT_IP": "1.1.1.1"}

    def test_context(self):
        context = self.view.get_context_data()
        self.assertIn("device_id", context)
        self.assertIn("device_role", context)
        self.assertIn("ip_address", context)

    def test_context_with_values(self):
        with override_settings(DEVICE_ID="10", DEVICE_ROLE=CLIENT):
            app_config = django_apps.get_app_config("edc_device")
            app_config.device_id = None
            app_config.device_role = None
            app_config.ready()
            context = self.view.get_context_data()
            self.assertEqual(context.get("device_id"), "10")
            self.assertEqual(context.get("device_role"), CLIENT)

    def test_context_ip(self):
        context = self.view.get_context_data()
        self.assertEqual(context.get("ip_address"), "1.1.1.1")

    def test_context_ip_missing_meta(self):
        del self.view.request.META
        context = self.view.get_context_data()
        self.assertEqual(context.get("ip_address"), None)
