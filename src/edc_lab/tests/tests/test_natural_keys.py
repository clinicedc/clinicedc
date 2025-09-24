from clinicedc_tests.mixins import SiteTestCaseMixin
from clinicedc_tests.utils import NaturalKeyTestHelper
from django.test import TestCase, override_settings, tag


@tag("lab")
@override_settings(SITE_ID=10)
class TestNaturalKey(SiteTestCaseMixin, TestCase):
    nk_test_helper = NaturalKeyTestHelper()

    def test_natural_key_attrs(self):
        self.nk_test_helper.nk_test_natural_key_attr("edc_lab")

    def test_get_by_natural_key_attr(self):
        self.nk_test_helper.nk_test_get_by_natural_key_attr("edc_lab")
