from django.test import TestCase

from ..medications import CapsuleDosage


class TestCapsuleDrugDosage(TestCase):
    def test_required_quantity(self):
        """Assert number of capsules."""
        capsule_dosage = CapsuleDosage(
            body_weight=40.0,
            strength=500,
            millgrams_per_capsule=100,
            duration=7,
            use_body_weight=True,
        )
        self.assertEqual(capsule_dosage.required_quantity, 56)

    def test_fluconazole_required_quantity1(self):
        """Assert number of capsules fluconacole."""
        capsule_dosage = CapsuleDosage(
            strength=200, millgrams_per_capsule=1200, duration=14, use_body_weight=False
        )
        self.assertEqual(capsule_dosage.required_quantity, 84)
