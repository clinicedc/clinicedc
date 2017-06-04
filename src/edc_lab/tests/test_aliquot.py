from django.db.utils import IntegrityError
from django.test import TestCase, tag

from ..lab import AliquotWrapper
from ..models import Aliquot


@tag('aliquot')
class TestAliquot(TestCase):

    def test_aliquot_model_constraint(self):
        Aliquot.objects.create(count=0)
        self.assertRaises(
            IntegrityError,
            aliquot=Aliquot.objects.create, count=0)


@tag('aliquot')
class TestAliquotObject(TestCase):

    def test_aliquot(self):
        aliquot = Aliquot.objects.create(aliquot_identifier='1111111', count=0)
        aliquot_obj = AliquotWrapper(model_obj=aliquot)
        self.assertEqual(aliquot_obj.children.all().count(), 0)
        self.assertEqual(aliquot_obj.aliquot_identifier, '1111111')

#     def test_create(self):
#         aliquot = Aliquot.objects.create(aliquot_identifier='1111111', count=0)
#         aliquot_obj = AliquotObject(model_obj=aliquot)
#         aliquot_obj.create_aliquots(process, numeric_code, aliquot_count)
