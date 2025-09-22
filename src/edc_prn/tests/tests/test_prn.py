from clinicedc_tests.sites import all_sites
from django.test import override_settings, tag
from django.test.testcases import TestCase
from django.urls.base import reverse

from edc_facility.import_holidays import import_holidays
from edc_prn.prn import Prn
from edc_prn.site_prn_forms import AlreadyRegistered, site_prn_forms
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites


@tag("prn")
@override_settings(SITE_ID=10)
class TestPrn(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def test_init(self):
        Prn(model="clinicedc_tests.crfthree")
        # pprint(show_namespaces())
        # pprint(show_urls())

    def test_add_url(self):
        prn = Prn(model="clinicedc_tests.crfthree")
        self.assertIsNone(prn.add_url_name)
        prn = Prn(
            model="clinicedc_tests.crfthree",
            url_namespace="clinicedc_tests_admin",
            allow_add=True,
        )
        self.assertEqual(
            prn.add_url_name, "clinicedc_tests_admin:clinicedc_tests_crfthree_add"
        )

    def test_changelist_url(self):
        prn = Prn(
            model="clinicedc_tests.crfthree",
            url_namespace="clinicedc_tests_admin",
        )
        self.assertEqual(
            prn.changelist_url_name,
            "clinicedc_tests_admin:clinicedc_tests_crfthree_changelist",
        )

    def test_reverse_add_url(self):
        prn = Prn(
            model="clinicedc_tests.crfthree",
            url_namespace="clinicedc_tests_admin",
            allow_add=True,
        )
        reverse(prn.add_url_name)

    def test_reverse_changelist_url(self):
        prn = Prn(
            model="clinicedc_tests.crfthree",
            url_namespace="clinicedc_tests_admin",
            allow_add=True,
        )
        reverse(prn.changelist_url_name)

    def test_verbose_name(self):
        prn = Prn(
            model="clinicedc_tests.crfthree",
            url_namespace="clinicedc_tests_admin",
            allow_add=True,
        )
        self.assertEqual(prn.verbose_name, "crf three")

        prn = Prn(
            model="clinicedc_tests.crfthree",
            url_namespace="clinicedc_tests_admin",
            verbose_name="crf three",
            allow_add=True,
        )
        self.assertEqual(prn.verbose_name, "crf three")

    def test_register(self):
        prn = Prn(
            model="clinicedc_tests.crfthree",
            url_namespace="clinicedc_tests_admin",
            verbose_name="crf three",
            allow_add=True,
        )
        site_prn_forms.register(prn)
        self.assertRaises(AlreadyRegistered, site_prn_forms.register, prn)
