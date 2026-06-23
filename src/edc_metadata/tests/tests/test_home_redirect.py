"""`edc_metadata:home_url` renders the edc_metadata ``HomeView`` (login required).

Previously this url redirected to the CrfMetadata changelist via a
``HomeRedirectView``; it now resolves to a login-protected ``HomeView``.
"""

from django.test import TestCase, override_settings, tag
from django.urls import reverse


@tag("metadata")
@override_settings(SITE_ID=10)
class TestHomeView(TestCase):
    def test_home_url_resolves(self):
        self.assertEqual(reverse("edc_metadata:home_url"), "/edc_metadata/")

    def test_home_url_requires_login(self):
        response = self.client.get(reverse("edc_metadata:home_url"), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])
