from django.conf import settings
from django.test import TestCase, tag  # noqa
from django_collect_offline.tests import OfflineTestHelper
from edc_sites.tests import SiteTestCaseMixin
from edc_sites.utils import add_or_update_django_sites


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


#     def test_deserialize_subject_screening(self):
#         ambition_screening = mommy.make_recipe(
#             'edc_lab.subjectscreening')
#         outgoing_transaction = OutgoingTransaction.objects.get(
#             tx_name=ambition_screening._meta.label_lower)
#         self.offline_test_helper.offline_test_deserialize(
#             ambition_screening, outgoing_transaction)
