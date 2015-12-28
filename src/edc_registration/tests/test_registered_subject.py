import re

from django.test import TestCase
from django.conf import settings

from ..models import RegisteredSubject

from .factories import RegisteredSubjectFactory
from edc_registration.models import RegisteredSubjectError
from django.test.utils import override_settings


class TestRegisterSubject(TestCase):

    def test_subject_identifier_uuid(self):
        """Tests the subject_identifier is a uuid by default"""
        registered_subject = RegisteredSubjectFactory()
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        self.assertTrue(re_pk.match(registered_subject.subject_identifier))
        self.assertTrue(re_pk.match(registered_subject.subject_identifier_as_pk))

    def test_subject_identifier_set(self):
        """Asserts subject_identifier_pk does not change when subject_identifier is set."""
        registered_subject = RegisteredSubjectFactory(subject_identifier='9999999-9')
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        self.assertTrue(re_pk.match(registered_subject.subject_identifier_as_pk))
        self.assertFalse(re_pk.match(registered_subject.subject_identifier))

    def test_create_duplicate(self):
        """Asserts raises on attempt to create duplicate"""
        RegisteredSubjectFactory(subject_identifier='9999999-9')
        self.assertRaises(RegisteredSubjectError, RegisteredSubjectFactory, subject_identifier='9999999-9')

    def test_create_duplicate2(self):
        """Asserts raises on attempt to create duplicate"""
        rs1 = RegisteredSubjectFactory()
        rs2 = RegisteredSubjectFactory()
        rs1.subject_identifier = '9999999-9'
        rs1.save()
        rs2.subject_identifier = '9999999-9'
        self.assertRaises(RegisteredSubjectError, rs2.save)

    def test_cannot_change_subject_identifier(self):
        """Asserts raises on attempt to create duplicate"""
        rs = RegisteredSubjectFactory(subject_identifier='9999999-9')
        rs.subject_identifier = '9999999-1'
        self.assertRaises(RegisteredSubjectError, rs.save)

    def test_defaults_max_subjects(self):
        rs = RegisteredSubjectFactory(subject_identifier='9999999-9')
        self.assertEqual(rs.max_subjects, {'subject': -1})

    @override_settings(MAX_SUBJECTS={'subject': 0})
    def test_raises_on_max_subjects(self):
        self.assertRaises(RegisteredSubjectError, RegisteredSubjectFactory, subject_identifier='9999999-9')

    @override_settings(MAX_SUBJECTS={'subject': 1})
    def test_raises_on_max_subjects2(self):
        RegisteredSubjectFactory(subject_identifier='9999999-9')
        self.assertRaises(RegisteredSubjectError, RegisteredSubjectFactory, subject_identifier='9999999-1')

    @override_settings(MAX_SUBJECTS={'subject': 2})
    def test_raises_on_max_subjects3(self):
        RegisteredSubjectFactory(subject_identifier='9999999-1')
        RegisteredSubjectFactory(subject_identifier='9999999-2')
        self.assertRaises(RegisteredSubjectError, RegisteredSubjectFactory, subject_identifier='9999999-3')

    @override_settings(MAX_SUBJECTS={'mother': 100, 'infant': -1}, SUBJECT_TYPES=['mother', 'infant'])
    def test_knows_subject_types(self):
        rs1 = RegisteredSubjectFactory(subject_identifier='9999999-9', subject_type='mother')
        RegisteredSubjectFactory(subject_identifier='9999999-9-10', subject_type='infant')
        self.assertEqual(rs1.max_subjects, {'mother': 100, 'infant': -1})
        self.assertEqual(rs1.subject_types, ['mother', 'infant'])

    @override_settings(MAX_SUBJECTS={'subject': 100}, SUBJECT_TYPES=['mother', 'infant'])
    def test_raises_on_incorrect_subjects(self):
        self.assertRaises(RegisteredSubjectError, RegisteredSubjectFactory, subject_identifier='9999999-9')
