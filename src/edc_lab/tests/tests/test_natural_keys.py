from django.conf import settings
from django.test import TestCase, tag  # noqa
from django_collect_offline.tests import OfflineTestHelper
from edc_sites.tests import SiteTestCaseMixin
from edc_sites import add_or_update_django_sites


class TestNaturalKey(SiteTestCaseMixin, TestCase):

    offline_test_helper = OfflineTestHelper()

    @classmethod
    def setUpClass(cls):
        add_or_update_django_sites(
            sites=((settings.SITE_ID, "test_site", "Test Site"),), fqdn="clinicedc.org"
        )
        return super().setUpClass()

    def tearDown(self):
        super().tearDown()

    def test_natural_key_attrs(self):
        self.offline_test_helper.offline_test_natural_key_attr("edc_lab")

    def test_get_by_natural_key_attr(self):
        self.offline_test_helper.offline_test_get_by_natural_key_attr("edc_lab")
