from django.test.testcases import TestCase
from django.urls.base import reverse

from edc_prn.prn import Prn
from edc_prn.site_prn_forms import AlreadyRegistered, site_prn_forms

# required for admin to load
from ..models import TestModel  # noqa


class TestPrn(TestCase):
    def test_init(self):
        Prn(model="edc_prn.testmodel")

    def test_add_url(self):
        prn = Prn(model="edc_prn.testmodel")
        self.assertIsNone(prn.add_url_name)
        prn = Prn(model="edc_prn.testmodel", allow_add=True)
        self.assertEqual(prn.add_url_name, "edc_prn_testmodel_add")

    def test_changelist_url(self):
        prn = Prn(model="edc_prn.testmodel")
        self.assertEqual(prn.changelist_url_name, "edc_prn_testmodel_changelist")

    def test_reverse_add_url(self):
        prn = Prn(model="edc_prn.testmodel", url_namespace="admin", allow_add=True)
        reverse(prn.add_url_name)

    def test_reverse_changelist_url(self):
        prn = Prn(model="edc_prn.testmodel", url_namespace="admin", allow_add=True)
        reverse(prn.changelist_url_name)

    def test_verbose_name(self):
        prn = Prn(model="edc_prn.testmodel", url_namespace="admin", allow_add=True)
        self.assertEqual(prn.verbose_name, "Test Model")

        prn = Prn(
            model="edc_prn.testmodel",
            url_namespace="admin",
            verbose_name="My Test Model",
            allow_add=True,
        )
        self.assertEqual(prn.verbose_name, "My Test Model")

    def test_register(self):
        prn = Prn(
            model="edc_prn.testmodel",
            url_namespace="admin",
            verbose_name="My Test Model",
            allow_add=True,
        )
        site_prn_forms.register(prn)
        self.assertRaises(AlreadyRegistered, site_prn_forms.register, prn)
