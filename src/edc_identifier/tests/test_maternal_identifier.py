from faker import Faker

from django.apps import apps as django_apps
from django.test import TestCase, tag

from ..maternal_identifier import MaternalIdentifier


fake = Faker()


@tag('maternal')
class TestMaternalIdentifier(TestCase):

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
