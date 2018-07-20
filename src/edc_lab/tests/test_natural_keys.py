from django.test import TestCase, tag
from django.test.utils import override_settings
from django_collect_offline.models import OutgoingTransaction
from django_collect_offline.tests import OfflineTestHelper
from edc_base.sites.utils import add_or_update_django_sites
from edc_base.tests import SiteTestCaseMixin
from model_mommy import mommy


class TestNaturalKey(SiteTestCaseMixin, TestCase):

    offline_test_helper = OfflineTestHelper()

    @classmethod
    def setUpClass(cls):
        add_or_update_django_sites(
            sites=((10, 'test_site', 'Test Site'), ), fqdn='clinicedc.org')
        return super().setUpClass()

    def tearDown(self):
        super().tearDown()

    def test_natural_key_attrs(self):
        self.offline_test_helper.offline_test_natural_key_attr(
            'edc_lab')

    def test_get_by_natural_key_attr(self):
        self.offline_test_helper.offline_test_get_by_natural_key_attr(
            'edc_lab')

#     def test_deserialize_subject_screening(self):
#         ambition_screening = mommy.make_recipe(
#             'edc_lab.subjectscreening')
#         outgoing_transaction = OutgoingTransaction.objects.get(
#             tx_name=ambition_screening._meta.label_lower)
#         self.offline_test_helper.offline_test_deserialize(
#             ambition_screening, outgoing_transaction)
