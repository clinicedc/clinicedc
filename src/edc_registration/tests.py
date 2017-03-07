import copy
import re

from dateutil.relativedelta import relativedelta
from model_mommy import mommy

from django.apps import apps as django_apps
from django.test import TestCase

from edc_base.utils import get_uuid
from edc_base_test.mixins import DatesTestMixin
from edc_example.factories import SubjectConsentFactory

from .exceptions import RegisteredSubjectError

RegisteredSubject = django_apps.get_app_config('edc_registration').model


class TestRegistration(DatesTestMixin, TestCase):

    def setUp(self):
        self.options = {
            'identity': '111111111',
            'confirm_identity': '111111111',
            'identity_type': 'OMANG',
            'study_site': '40'
        }
        # put in a few records ...
        options = copy.copy(self.options)
        del options['confirm_identity']
        for i in range(3, 8):
            options.update({'identity': '11111111{}'.format(i)})
            RegisteredSubject.objects.create(**options)
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            consent_datetime=self.get_utcnow(),
            **self.options)
        self.assertTrue(subject_consent.subject_identifier)
        self.registered_subject = RegisteredSubject.objects.get(
            subject_identifier=subject_consent.subject_identifier,
            identity='111111111')

    def test_subject_identifier_uuid(self):
        """Tests the subject_identifier is a uuid by default"""
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        registered_subject = mommy.make_recipe(
            'edc_registration.registeredsubject',
            identity='111111112',
            identity_type='OMANG')
        self.assertTrue(re_pk.match(registered_subject.subject_identifier))
        self.assertTrue(re_pk.match(registered_subject.subject_identifier_as_pk))

    def test_subject_identifier_set(self):
        """Asserts subject_identifier_pk does not change when subject_identifier is set."""
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        registered_subject = mommy.make_recipe(
            'edc_registration.registeredsubject',
            identity='111111112',
            identity_type='OMANG',
            subject_identifier=None)
        subject_identifier_as_pk = registered_subject.subject_identifier_as_pk
        self.assertTrue(re_pk.match(subject_identifier_as_pk))
        registered_subject.subject_identifier = '999999999'
        registered_subject.save()
        registered_subject = RegisteredSubject.objects.get(subject_identifier_as_pk=subject_identifier_as_pk)
        self.assertFalse(re_pk.match(registered_subject.subject_identifier))
        self.assertEqual(subject_identifier_as_pk, registered_subject.subject_identifier_as_pk)

    def test_create_duplicate(self):
        """Asserts raises on attempt to create duplicate"""
        self.assertEqual(RegisteredSubject.objects.filter(identity='111111111').count(), 1)
        self.assertRaises(
            RegisteredSubjectError,
            mommy.make_recipe,
            'edc_registration.registeredsubject',
            identity='111111111',
            identity_type='OMANG')

    def test_create_duplicate2(self):
        """Asserts raises on attempt to create duplicate"""
        RegisteredSubject = django_apps.get_app_config('edc_registration').model
        options = copy.copy(self.options)
        del options['confirm_identity']
        registered_subject_dupl = RegisteredSubject(**options)
        self.assertRaises(RegisteredSubjectError, registered_subject_dupl.save)

    def test_create_duplicate3(self):
        """Asserts raises on attempt to create duplicate"""
        RegisteredSubject = django_apps.get_app_config('edc_registration').model
        options = copy.copy(self.options)
        del options['confirm_identity']
        self.assertEqual(RegisteredSubject.objects.filter(identity='111111111').count(), 1)
        self.assertRaises(
            RegisteredSubjectError,
            mommy.make_recipe,
            'edc_registration.registeredsubject',
            **options)

    def test_cannot_change_subject_identifier(self):
        """Asserts raises on attempt to create duplicate"""
        self.registered_subject.subject_identifier = '9999999-1'
        self.assertRaises(RegisteredSubjectError, self.registered_subject.save)

    def test_registration_creates(self):
        self.options.update(
            dict(
                identity='111211111',
                confirm_identity='111211111',
                dob=(self.get_utcnow() - relativedelta(years=25)).date(),
                first_name='ERIK',
                last_name='OBAMA',
                initials='EO',
                subject_identifier=str(get_uuid())))
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            consent_datetime=self.get_utcnow(),
            **self.options)
        self.assertEqual(subject_consent.registration_model.objects.filter(identity='111211111').count(), 1)
        subject_consent.save()
        self.assertEqual(subject_consent.registration_model.objects.filter(identity='111211111').count(), 1)

    def test_registration_updates(self):
        self.options.update(
            dict(
                identity='111211111',
                confirm_identity='111211111',
                dob=(self.get_utcnow() - relativedelta(years=25)).date(),
                first_name='ERIK',
                last_name='OBAMA',
                initials='EO',
                subject_identifier=str(get_uuid())))
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            consent_datetime=self.get_utcnow(),
            **self.options)
        self.assertEqual(subject_consent.registration_model.objects.filter(identity='111211111').count(), 1)
        subject_consent.first_name = 'BARACK'
        subject_consent.save()
        self.assertEqual(subject_consent.registration_model.objects.filter(identity='111211111').count(), 1)
        registration = subject_consent.registration_model.objects.get(identity='111211111')
        self.assertEqual(registration.first_name, 'BARACK')
