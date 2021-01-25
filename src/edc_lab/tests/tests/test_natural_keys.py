from django.conf import settings
from django.test import TestCase, tag  # noqa
from edc_test_utils.natural_key_test_helper import NaturalKeyTestHelper
from edc_sites.single_site import SingleSite
from edc_sites.tests import SiteTestCaseMixin
from edc_sites import add_or_update_django_sites


class TestNaturalKey(SiteTestCaseMixin, TestCase):

    nk_test_helper = NaturalKeyTestHelper()

    @classmethod
    def setUpClass(cls):
        add_or_update_django_sites(
            sites=[
                SingleSite(
                    settings.SITE_ID,
                    "test_site",
                    country_code="ug",
                    country="uganda",
                    domain="bugamba.ug.clinicedc.org",
                )
            ]
        )
        return super().setUpClass()

    def test_natural_key_attrs(self):
        self.nk_test_helper.nk_test_natural_key_attr("edc_lab")

    def test_get_by_natural_key_attr(self):
        self.nk_test_helper.nk_test_get_by_natural_key_attr("edc_lab")
