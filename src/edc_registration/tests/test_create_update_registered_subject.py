import copy
import re

from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.test import TestCase
from edc_base.utils import get_uuid, get_utcnow

from ..exceptions import RegisteredSubjectError
from .models import SubjectEligibility, SubjectConsent
RegisteredSubject = django_apps.get_app_config('edc_registration').model


class TestRegistration(TestCase):

    def setUp(self):
        self.subject_eligibility = SubjectEligibility.objects.create(
            screening_identifier='12345')
        self.options = {
            'identity': '111111111',
            'identity_type': 'OMANG',
            'study_site': '40'
        }
        self.registered_subject = RegisteredSubject.objects.get(
            registration_identifier=self.subject_eligibility.screening_identifier)

    def test_subject_identifier_uuid(self):
        """Tests the subject_identifier is a uuid by default"""
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        self.assertEqual(RegisteredSubject.objects.all().count(), 1)
        self.assertTrue(
            re_pk.match(str(self.registered_subject.subject_identifier_as_pk)))

    def test_subject_identifier_set(self):
        """Asserts subject_identifier_pk does not change when subject_identifier is set."""
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        subject_identifier_as_pk = self.registered_subject.subject_identifier_as_pk
        self.assertTrue(re_pk.match(str(subject_identifier_as_pk)))
        self.registered_subject.subject_identifier = '999999999'
        self.registered_subject.save()
        registered_subject = RegisteredSubject.objects.get(
            subject_identifier_as_pk=subject_identifier_as_pk)
        self.assertEqual(
            subject_identifier_as_pk, registered_subject.subject_identifier_as_pk)

    def test_create_duplicate(self):
        """Asserts raises on attempt to create duplicate"""
        RegisteredSubject.objects.filter(
            registration_identifier=self.subject_eligibility.screening_identifier
        ).update(**self.options)
        self.assertEqual(
            RegisteredSubject.objects.filter(identity='111111111').count(), 1)

        self.assertRaises(
            RegisteredSubjectError,
            RegisteredSubject.objects.create,
            **self.options)

    def test_create_duplicate2(self):
        """Asserts raises on attempt to create duplicate"""
        RegisteredSubject.objects.filter(
            registration_identifier=self.subject_eligibility.screening_identifier
        ).update(**self.options)
        options = copy.copy(self.options)
        registered_subject_dupl = RegisteredSubject(**options)
        self.assertRaises(RegisteredSubjectError, registered_subject_dupl.save)

    def test_create_duplicate3(self):
        """Asserts raises on attempt to create duplicate"""
        RegisteredSubject.objects.filter(
            registration_identifier=self.subject_eligibility.screening_identifier
        ).update(**self.options)
        self.assertEqual(
            RegisteredSubject.objects.filter(identity='111111111').count(), 1)
        self.assertRaises(
            RegisteredSubjectError,
            RegisteredSubject.objects.create,
            **self.options)

    def test_cannot_change_subject_identifier(self):
        """Asserts raises on attempt to create duplicate"""
        self.registered_subject.subject_identifier = '9999999-1'
        self.registered_subject.save()
        self.registered_subject.subject_identifier = '9998888-3'
        self.assertRaises(RegisteredSubjectError, self.registered_subject.save)

    def test_registration_creates(self):
        self.options.update(
            dict(
                identity='111211111',
                dob=(get_utcnow() - relativedelta(years=25)).date(),
                first_name='ERIK',
                last_name='OBAMA',
                screening_identifier=self.subject_eligibility.screening_identifier,
                initials='EO'))
        subject_consent = SubjectConsent.objects.create(
            **self.options)
        self.assertEqual(subject_consent.registration_model.objects.filter(
            identity='111211111').count(), 1)
        subject_consent = SubjectConsent.objects.get(identity='111211111')
        subject_consent.save()
        self.assertEqual(subject_consent.registration_model.objects.filter(
            identity='111211111').count(), 1)

    def test_registration_updates(self):
        self.options.update(
            dict(
                identity='111211111',
                dob=(get_utcnow() - relativedelta(years=25)).date(),
                first_name='ERIK',
                last_name='OBAMA',
                initials='EO',
                screening_identifier=self.subject_eligibility.screening_identifier))
        subject_consent = SubjectConsent.objects.create(
            **self.options)
        self.assertEqual(subject_consent.registration_model.objects.filter(
            identity='111211111').count(), 1)
        subject_consent.first_name = 'BARACK'
        subject_consent.save()
        self.assertEqual(subject_consent.registration_model.objects.filter(
            identity='111211111').count(), 1)
        registration = subject_consent.registration_model.objects.get(
            identity='111211111')
        self.assertEqual(registration.first_name, 'BARACK')
