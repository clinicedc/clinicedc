from django.test import TestCase, tag

from ..lab import Specimen


@tag('sepcimen')
class TestSpecimen(TestCase):

    def test_specimen(self):
        Specimen()
