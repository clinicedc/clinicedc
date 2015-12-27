from django.test import TestCase
from .factories import RegisteredSubjectFactory


class FactoryTests(TestCase):

    def test_p1(self):
        "Tests data factories."
        self.assertIsNotNone(RegisteredSubjectFactory().subject_identifier)
        print RegisteredSubjectFactory().subject_identifier
        print RegisteredSubjectFactory().subject_identifier
        print RegisteredSubjectFactory().subject_identifier
