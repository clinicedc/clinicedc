from django.test import TestCase
from django.conf import settings

from edc_identifier.exceptions import IdentifierError

from ..models import RegisteredSubject

from .factories.registered_subject_factory import RegisteredSubjectFactory


class RegisteredSubjectsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        pass

    def tearDown(self):
        RegisteredSubject.objects.all().delete()

    def test_set_dummy_identifiers(self):
        """Test setting dummy identifiers"""
        reg = RegisteredSubjectFactory.build()
        reg.insert_dummy_identifier()
        self.assertEquals(reg.subject_identifier, "")
        reg.dummy_subject_identifier()
        self.assertGreater(len(reg.subject_identifier), 0, "Subject identifier not set")

    def test_duplicate_identifier(self):
        """Test that duplicate subject identifiers will not be allowed"""
        subject1 = RegisteredSubjectFactory()
        subject2 = RegisteredSubjectFactory.build()
        subject2.subject_identifier=subject1.subject_identifier
        self.assertRaises(IdentifierError, subject2.save)
