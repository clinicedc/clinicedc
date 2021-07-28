from django.apps import apps as django_apps
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from edc_device.constants import CLIENT
from edc_device.views import HomeView


@override_settings(DEBUG=False, LIVE_SYSTEM=True)
class TestHomeView(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="erik")
        self.view = HomeView()
        self.client.force_login(self.user)
        self.response = self.client.get(reverse("edc_device:home_url"))

    def test_context(self):
        self.assertIn("project_name", self.response.context)
        self.assertIn("device_id", self.response.context)
        self.assertIn("device_role", self.response.context)
        self.assertIn("ip_address", self.response.context)

    def test_context_with_values(self):
        with override_settings(DEVICE_ID="10", DEVICE_ROLE=CLIENT):
            app_config = django_apps.get_app_config("edc_device")
            app_config.device_id = None
            app_config.device_role = None
            app_config.ready()
            self.client.force_login(self.user)
            response = self.client.get(reverse("edc_device:home_url"))
            self.assertEqual(response.context.get("device_id"), "10")
            self.assertEqual(response.context.get("device_role"), CLIENT)

    def test_context_ip(self):
        self.assertIsNotNone(self.response.context.get("ip_address"))
