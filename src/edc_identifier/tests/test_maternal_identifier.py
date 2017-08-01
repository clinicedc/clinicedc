from faker import Faker

from django.apps import apps as django_apps
from django.test import TestCase, tag
from edc_protocol import SubjectType, Cap

from ..maternal_identifier import MaternalIdentifier


fake = Faker()


@tag('maternal')
class TestMaternalIdentifier(TestCase):

    def setUp(self):
        app_config = django_apps.get_app_config('edc_protocol')
        app_config.subject_types = [
            SubjectType('subject', 'Research Subjects', Cap(
                model_name='edc_identifier.enrollment', max_subjects=9999)),
            SubjectType('subject', 'Research Subjects', Cap(
                model_name='edc_identifier.enrollmentthree', max_subjects=5))
        ]
        app_config.site_code = '10'
        app_config.site_name = 'test_site'
        app_config.ready()

    def test_create(self):
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name())
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')

    def test_creates_registered_subject(self):
        RegisteredSubject = django_apps.get_app_config(
            'edc_registration').model
        MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        try:
            RegisteredSubject.objects.get(subject_identifier='000-40990001-6')
        except RegisteredSubject.DoesNotExist:
            self.fail('RegisteredSubject.DoesNotExist unexpectedly raised')

    def test_creates_registered_subject_attrs(self):
        RegisteredSubject = django_apps.get_app_config(
            'edc_registration').model
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertIsNotNone(maternal_identifier.identifier)
        obj = RegisteredSubject.objects.get(
            subject_identifier='000-40990001-6')
        self.assertEqual(obj.study_site, '40')
        self.assertEqual(obj.subject_type, 'subject')
        self.assertIsNotNone(obj.last_name)
