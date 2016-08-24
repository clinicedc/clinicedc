import re

from django.apps import apps as django_apps
from django.test import TestCase

from edc_registration.exceptions import RegisteredSubjectError


class TestRegisterSubject(TestCase):

    def setUp(self):
        app_config = django_apps.get_app_config('edc_registration')
        RegisteredSubject = app_config.model
        self.subject_identifier = '9999999-9'
        self.model = RegisteredSubject
        self.options = {
            'identity': '111111111',
            'identity_type': 'OMANG',
            'subject_identifier': self.subject_identifier,
        }
        self.registered_subject = self.model.objects.create(**self.options)
        self.registered_subject = self.model.objects.get(subject_identifier=self.subject_identifier)

    def test_subject_identifier_uuid(self):
        """Tests the subject_identifier is a uuid by default"""
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        app_config = django_apps.get_app_config('edc_registration')
        RegisteredSubject = app_config.model
        self.model = RegisteredSubject
        self.options = {
            'identity': '111111111',
            'identity_type': 'OMANG',
        }
        registered_subject = self.model.objects.create(**self.options)
        self.assertTrue(re_pk.match(registered_subject.subject_identifier))
        self.assertTrue(re_pk.match(registered_subject.subject_identifier_as_pk))

    def test_subject_identifier_set(self):
        """Asserts subject_identifier_pk does not change when subject_identifier is set."""
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        self.assertTrue(re_pk.match(self.registered_subject.subject_identifier_as_pk))
        self.assertFalse(re_pk.match(self.registered_subject.subject_identifier))

    def test_create_duplicate(self):
        """Asserts raises on attempt to create duplicate"""
        self.assertRaises(RegisteredSubjectError, self.model.objects.create, **self.options)

    def test_create_duplicate2(self):
        """Asserts raises on attempt to create duplicate"""
        registered_subject_dupl = self.model(**self.options)
        self.assertRaises(RegisteredSubjectError, registered_subject_dupl.save)

    def test_cannot_change_subject_identifier(self):
        """Asserts raises on attempt to create duplicate"""
        self.registered_subject.subject_identifier = '9999999-1'
        self.assertRaises(RegisteredSubjectError, self.registered_subject.save)
