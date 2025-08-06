from django.test import TestCase, override_settings
from edc_sites.tests import SiteTestCaseMixin
from edc_test_utils.natural_key_test_helper import NaturalKeyTestHelper


@override_settings(SITE_ID=10)
class TestNaturalKey(SiteTestCaseMixin, TestCase):
    nk_test_helper = NaturalKeyTestHelper()

    def test_natural_key_attrs(self):
        self.nk_test_helper.nk_test_natural_key_attr("edc_lab")

    def test_get_by_natural_key_attr(self):
        self.nk_test_helper.nk_test_get_by_natural_key_attr("edc_lab")
