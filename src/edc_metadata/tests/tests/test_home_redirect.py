"""Prove that `edc_metadata:home_url` redirects to the CrfMetadata
changelist with `?entry_status__exact=REQUIRED` prefilled.

This is the entry point the `administration.html` section uses for
"Data Collection Status" (via `AdministrationViewMixin.get_section`,
which resolves `edc_metadata:home_url` when `AppConfig.home_url_name`
is not set — and it isn't).
"""

from django.test import TestCase, override_settings, tag
from django.urls import reverse

from edc_metadata.constants import REQUIRED


@tag("metadata")
@override_settings(SITE_ID=10)
class TestHomeRedirect(TestCase):
    def test_home_url_resolves(self):
        self.assertEqual(reverse("edc_metadata:home_url"), "/edc_metadata/")

    def test_home_url_redirects_to_crfmetadata_with_required_filter(self):
        response = self.client.get(reverse("edc_metadata:home_url"), follow=False)
        self.assertEqual(response.status_code, 302)
        expected_path = reverse("edc_metadata_admin:edc_metadata_crfmetadata_changelist")
        self.assertEqual(
            response["Location"],
            f"{expected_path}?entry_status__exact={REQUIRED}",
        )
