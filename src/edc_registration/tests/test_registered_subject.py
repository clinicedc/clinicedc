from django.test import TestCase
from django.conf import settings

from .factories.registered_subject_factory import RegisteredSubjectFactory


class RegisteredSubjectsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        pass

    def tearDown(self):
        pass

    def test_set_dummy_identifiers(self):
        """Test setting dummy identifiers"""
        reg = RegisteredSubjectFactory.build()
        reg.insert_dummy_identifier()
        self.assertEquals(reg.subject_identifier, "")
        reg.dummy_subject_identifier()
        self.assertGreater(len(reg.subject_identifier), 0, "Subject identifier not set")
