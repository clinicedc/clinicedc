from django.db.utils import IntegrityError
from django.test import TestCase, tag

from ..lab import AliquotCreator, AliquotCreatorError
from ..models import Aliquot


@tag('aliquot')
class TestAliquot(TestCase):

    def test_aliquot_model_constraint(self):
        Aliquot.objects.create(count=0)
        self.assertRaises(
            IntegrityError,
            aliquot=Aliquot.objects.create, count=0)

    def test_create_aliquot(self):
        self.assertRaises(AliquotCreatorError, AliquotCreator)
