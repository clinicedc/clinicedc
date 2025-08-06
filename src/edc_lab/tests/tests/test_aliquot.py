from django.db.utils import IntegrityError
from django.test import TestCase, override_settings
from edc_sites.tests import SiteTestCaseMixin

from edc_lab.lab import AliquotCreator, AliquotCreatorError
from edc_lab.models import Aliquot


@override_settings(SITE_ID=10)
class TestAliquot(SiteTestCaseMixin, TestCase):
    def test_aliquot_model_constraint(self):
        Aliquot.objects.create(count=0)
        self.assertRaises(IntegrityError, Aliquot.objects.create, count=0)

    def test_create_aliquot(self):
        self.assertRaises(AliquotCreatorError, AliquotCreator)
