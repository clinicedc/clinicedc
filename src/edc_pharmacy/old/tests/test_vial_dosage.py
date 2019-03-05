from decimal import Decimal

from django.test import TestCase, tag

from ..medications import CapsuleDosage, VialDosage


@tag("test_vial")
class TestVialDosage(TestCase):
    def test_round(self):
        vial_dosage = VialDosage()
        self.assertEqual(vial_dosage.round(value=1.2), 2)

    def test_round_1(self):
        capsule_dosage = CapsuleDosage()
        self.assertEqual(capsule_dosage.round(value=1.7), 2)

    def test_required_quantity(self):
        """Assert number of vialz. (Single Dose)."""
        capsule_dosage = VialDosage(
            body_weight=40.0,
            strength_of_vial=50,
            millgrams_per_vial=10,
            duration=1,
            use_body_weight=True,
        )
        self.assertEqual(capsule_dosage.required_quantity, 8)

    def test_amphoterin(self):
        """Assert number of vialz for amphoterin."""
        capsule_dosage = VialDosage(
            body_weight=40.0,
            strength_of_vial=50,
            millgrams_per_vial=1,
            duration=7,
            use_body_weight=True,
        )
        self.assertEqual(capsule_dosage.required_quantity, 7)

    def test_amphoterin_1(self):
        """Assert number of vialz for amphoterin."""
        body_weight = Decimal("40.00")
        capsule_dosage = VialDosage(
            body_weight=body_weight,
            strength_of_vial=50,
            millgrams_per_vial=1,
            duration=7,
            use_body_weight=True,
        )
        self.assertEqual(capsule_dosage.required_quantity, 7)
