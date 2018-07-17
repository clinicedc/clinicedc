from django.db.utils import IntegrityError
from django.test import TestCase, tag
from edc_base.sites.utils import add_or_update_django_sites

from ..lab import AliquotCreator, AliquotCreatorError
from ..models import Aliquot


class TestAliquot(TestCase):

    @classmethod
    def setUpClass(cls):
        add_or_update_django_sites(
            sites=((10, 'test_site', 'Test Site'), ), fqdn='clinicedc.org')
        return super().setUpClass()

    def tearDown(self):
        super().tearDown()

    def test_aliquot_model_constraint(self):
        Aliquot.objects.create(count=0)
        self.assertRaises(
            IntegrityError,
            aliquot=Aliquot.objects.create, count=0)

    def test_create_aliquot(self):
        self.assertRaises(AliquotCreatorError, AliquotCreator)
