from django.conf import settings
from django.db.utils import IntegrityError
from django.test import TestCase, tag  # noqa
from edc_sites import add_or_update_django_sites

from edc_lab.lab import AliquotCreator, AliquotCreatorError
from edc_lab.models import Aliquot
from edc_sites.tests import SiteTestCaseMixin


class TestAliquot(SiteTestCaseMixin, TestCase):
    def setUp(self):
        add_or_update_django_sites(sites=self.default_sites, verbose=False)

    def tearDown(self):
        super().tearDown()

    def test_aliquot_model_constraint(self):
        Aliquot.objects.create(count=0)
        self.assertRaises(IntegrityError, Aliquot.objects.create, count=0)

    def test_create_aliquot(self):
        self.assertRaises(AliquotCreatorError, AliquotCreator)
