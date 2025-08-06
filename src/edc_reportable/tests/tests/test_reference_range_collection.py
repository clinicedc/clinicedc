from django.test import TestCase

from edc_reportable.models import ReferenceRangeCollection


class TestReferenceRangeCollection(TestCase):
    def test_ok(self):
        obj = ReferenceRangeCollection.objects.create(
            name="Test Reference Range Collection",
            grade1=False,
            grade2=False,
            grade3=True,
            grade4=True,
        )
        self.assertEqual(obj.grades("sodium"), [3, 4])
