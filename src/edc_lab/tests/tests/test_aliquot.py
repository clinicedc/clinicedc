from django.conf import settings
from django.db.utils import IntegrityError
from django.test import TestCase, tag  # noqa
from edc_sites import add_or_update_django_sites

from edc_lab.lab import AliquotCreator, AliquotCreatorError
from edc_lab.models import Aliquot
from edc_sites.single_site import SingleSite
from edc_sites.tests import SiteTestCaseMixin


class TestAliquot(SiteTestCaseMixin, TestCase):
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

    def test_aliquot_model_constraint(self):
        Aliquot.objects.create(count=0)
        self.assertRaises(IntegrityError, Aliquot.objects.create, count=0)

    def test_create_aliquot(self):
        self.assertRaises(AliquotCreatorError, AliquotCreator)
