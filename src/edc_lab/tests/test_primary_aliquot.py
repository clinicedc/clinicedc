from django.test import TestCase, tag

from ..lab import PrimaryAliquot, AliquotType
from ..models import Aliquot


@tag('primary')
class TestPrimaryAliquot(TestCase):

    def test_primary_aliquot(self):
        aliquot_type = AliquotType(
            name='aliquot_a', numeric_code='22', alpha_code='WW')
        p = PrimaryAliquot(
            requisition_identifier='ABCDE',
            identifier_prefix='066ABCDE',
            aliquot_model=Aliquot,
            aliquot_type=aliquot_type,
            length=16,
            count_padding=2)
        self.assertTrue(p.object)

    def test_primary_aliquot_exists(self):
        """Asserts primary aliquot exists using identifier_prefix.
        """
        aliquot_type = AliquotType(
            name='aliquot_a', numeric_code='22', alpha_code='WW')
        primary_aliquot = PrimaryAliquot(
            requisition_identifier='ABCDE',
            identifier_prefix='066ABCDE',
            aliquot_model=Aliquot,
            aliquot_type=aliquot_type,
            length=16,
            count_padding=2)
        obj = primary_aliquot.object
        p = PrimaryAliquot(
            identifier_prefix=obj.identifier_prefix,
            aliquot_model=Aliquot)
        self.assertEqual(obj.aliquot_identifier, p.object.aliquot_identifier)

    def test_primary_aliquot_exists2(self):
        """Asserts primary aliquot exists using requisition_identifier.
        """
        aliquot_type = AliquotType(
            name='aliquot_a', numeric_code='22', alpha_code='WW')
        primary_aliquot = PrimaryAliquot(
            requisition_identifier='ABCDE',
            identifier_prefix='066ABCDE',
            aliquot_model=Aliquot,
            aliquot_type=aliquot_type,
            length=16,
            count_padding=2)
        obj = primary_aliquot.object
        p = PrimaryAliquot(
            requisition_identifier=obj.requisition_identifier,
            aliquot_model=Aliquot)
        self.assertEqual(obj.aliquot_identifier, p.object.aliquot_identifier)

    def test_str(self):
        aliquot_type = AliquotType(
            name='aliquot_a', numeric_code='22', alpha_code='WW')
        primary_aliquot = PrimaryAliquot(
            requisition_identifier='ABCDE',
            identifier_prefix='066ABCDE',
            aliquot_model=Aliquot,
            aliquot_type=aliquot_type,
            length=16,
            count_padding=2)
        self.assertTrue(str(primary_aliquot))
