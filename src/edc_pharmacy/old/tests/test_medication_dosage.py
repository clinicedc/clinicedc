from edc_pharma.medications import medications

from django.test import TestCase

from ..medications import MedicationDosage


class TestMedicationDosage(TestCase):
    def test_repr(self):
        amphotericin = medications.get("amphotericin")
        med = MedicationDosage(medication_definition=amphotericin)
        self.assertTrue(med.__repr__())

    def test_quantity_amphotericin(self):
        amphotericin = medications.get("amphotericin")
        med = MedicationDosage(
            medication_definition=amphotericin, weight=40.0, duration=7
        )
        self.assertEqual(med.required_quantity, 7)

    def test_quantity_flucytosine(self):
        flucytosine = medications.get("flucytosine")
        med = MedicationDosage(medication_definition=flucytosine, weight=40, duration=7)
        self.assertEqual(med.required_quantity, 56)

    def test_quantity_single_dose_arm(self):
        ambisome = medications.get("ambisome")
        med = MedicationDosage(medication_definition=ambisome, weight=40.0, duration=1)
        self.assertEqual(med.required_quantity, 8)
