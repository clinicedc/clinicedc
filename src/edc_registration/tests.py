import copy
import re
from uuid import uuid4

from django.apps import apps as django_apps
from django.test import TestCase

from edc_registration.exceptions import RegisteredSubjectError
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from edc_example.factories import SubjectConsentFactory


class TestRegistration(TestCase):

    def setUp(self):
        app_config = django_apps.get_app_config('edc_registration')
        RegisteredSubject = app_config.model
        self.model = RegisteredSubject
        self.options = {
            'identity': '111111111',
            'confirm_identity': '111111111',
            'identity_type': 'OMANG',
        }
        subject_consent = SubjectConsentFactory(**self.options)
        self.assertTrue(subject_consent.subject_identifier)
        self.registered_subject = RegisteredSubject.objects.get(
            subject_identifier=subject_consent.subject_identifier,
            identity='111111111')

    def test_subject_identifier_uuid(self):
        """Tests the subject_identifier is a uuid by default"""
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        app_config = django_apps.get_app_config('edc_registration')
        RegisteredSubject = app_config.model
        self.options = {
            'identity': '111111112',
            'identity_type': 'OMANG',
        }
        registered_subject = RegisteredSubject.objects.create(**self.options)
        self.assertTrue(re_pk.match(registered_subject.subject_identifier))
        self.assertTrue(re_pk.match(registered_subject.subject_identifier_as_pk))

    def test_subject_identifier_set(self):
        """Asserts subject_identifier_pk does not change when subject_identifier is set."""
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        app_config = django_apps.get_app_config('edc_registration')
        RegisteredSubject = app_config.model
        self.options = {
            'identity': '111111112',
            'identity_type': 'OMANG',
        }
        registered_subject = RegisteredSubject.objects.create(**self.options)
        subject_identifier_as_pk = registered_subject.subject_identifier_as_pk
        self.assertTrue(re_pk.match(subject_identifier_as_pk))
        registered_subject.subject_identifier = '999999999'
        registered_subject.save()
        registered_subject = RegisteredSubject.objects.get(subject_identifier_as_pk=subject_identifier_as_pk)
        self.assertFalse(re_pk.match(registered_subject.subject_identifier))
        self.assertEqual(subject_identifier_as_pk, registered_subject.subject_identifier_as_pk)

    def test_create_duplicate(self):
        """Asserts raises on attempt to create duplicate"""
        options = copy.copy(self.options)
        del options['confirm_identity']
        app_config = django_apps.get_app_config('edc_registration')
        RegisteredSubject = app_config.model
        self.assertEqual(RegisteredSubject.objects.filter(identity='111111111').count(), 1)
        self.assertRaises(RegisteredSubjectError, RegisteredSubject.objects.create, **options)

    def test_create_duplicate2(self):
        """Asserts raises on attempt to create duplicate"""
        options = copy.copy(self.options)
        del options['confirm_identity']
        registered_subject_dupl = self.model(**options)
        self.assertRaises(RegisteredSubjectError, registered_subject_dupl.save)

    def test_cannot_change_subject_identifier(self):
        """Asserts raises on attempt to create duplicate"""
        self.registered_subject.subject_identifier = '9999999-1'
        self.assertRaises(RegisteredSubjectError, self.registered_subject.save)

    def test_registration_creates(self):
        self.options.update(
            dict(
                identity='111211111',
                confirm_identity='111211111',
                dob=timezone.now() - relativedelta(years=25),
                first_name='ERIK',
                last_name='OBAMA',
                initials='EO',
                subject_identifier=str(uuid4())))
        subject_consent = SubjectConsentFactory(**self.options)
        self.assertEqual(subject_consent.registration_model.objects.filter(identity='111211111').count(), 1)
        subject_consent.save()
        self.assertEqual(subject_consent.registration_model.objects.filter(identity='111211111').count(), 1)

    def test_registration_updates(self):
        self.options.update(
            dict(
                identity='111211111',
                confirm_identity='111211111',
                dob=timezone.now() - relativedelta(years=25),
                first_name='ERIK',
                last_name='OBAMA',
                initials='EO',
                subject_identifier=str(uuid4())))
        subject_consent = SubjectConsentFactory(**self.options)
        self.assertEqual(subject_consent.registration_model.objects.filter(identity='111211111').count(), 1)
        subject_consent.first_name = 'BARACK'
        subject_consent.save()
        self.assertEqual(subject_consent.registration_model.objects.filter(identity='111211111').count(), 1)
        registration = subject_consent.registration_model.objects.get(identity='111211111')
        self.assertEqual(registration.first_name, 'BARACK')
