from django.test import TestCase, tag
from edc_list_data.preload_data import PreloadData

from ..list_data import list_data
from ..models import Antibiotic, Neurological, Symptom, SignificantNewDiagnosis


class TestPreload(TestCase):
    def test_preload(self):

        PreloadData(list_data=list_data)

        self.assertEqual(Antibiotic.objects.all().count(), 8)
        self.assertEqual(Neurological.objects.all().count(), 9)
        self.assertEqual(Symptom.objects.all().count(), 17)
        self.assertEqual(SignificantNewDiagnosis.objects.all().count(), 8)
