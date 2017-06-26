from faker import Faker

from django.apps import apps as django_apps
from django.test import TestCase, tag
from edc_protocol import SubjectType, Cap

from ..models import IdentifierModel
from ..maternal_identifier import MaternalIdentifier


fake = Faker()


class TestIdentifierError(Exception):
    pass


@tag('infant')
class TestInfantIdentifier(TestCase):
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

    def test_create_singleton(self):
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(1, model='edc_identifier.maternallabdel')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-10')

    def test_create_twins(self):
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(2, model='edc_identifier.maternallabdel')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-25')
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-26')

    def test_create_triplets(self):
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(3, model='edc_identifier.maternallabdel')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-36')
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-37')
        self.assertEqual(
            maternal_identifier.infants[2].identifier, '000-40990001-6-38')

    def test_create_triplets_only_registered_2nd_born_as_list(self):
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(
            3, model='edc_identifier.maternallabdel', birth_orders=[2])
        self.assertEqual(maternal_identifier.infants[0].identifier, None)
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-37')
        self.assertEqual(maternal_identifier.infants[2].identifier, None)
        self.assertEqual(len(maternal_identifier.infants), 3)

    def test_create_triplets_only_registered_2nd_born(self):
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(
            3, model='edc_identifier.maternallabdel', birth_orders='2')
        self.assertEqual(maternal_identifier.infants[0].identifier, None)
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-37')
        self.assertEqual(maternal_identifier.infants[2].identifier, None)
        self.assertEqual(len(maternal_identifier.infants), 3)

    def test_create_triplets_only_registered_1st_born(self):
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(
            3, model='edc_identifier.maternallabdel', birth_orders='1')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-36')
        self.assertEqual(maternal_identifier.infants[1].identifier, None)
        self.assertEqual(maternal_identifier.infants[2].identifier, None)
        self.assertEqual(len(maternal_identifier.infants), 3)

    def test_create_triplets_only_registered_all_explicitly(self):
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(
            3, model='edc_identifier.maternallabdel', birth_orders='1,2,3')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-36')
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-37')
        self.assertEqual(
            maternal_identifier.infants[2].identifier, '000-40990001-6-38')
        self.assertEqual(len(maternal_identifier.infants), 3)

    def test_create_triplets_only_registered_all_by_default(self):
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(
            3, model='edc_identifier.maternallabdel', birth_orders=None)
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-36')
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-37')
        self.assertEqual(
            maternal_identifier.infants[2].identifier, '000-40990001-6-38')
        self.assertEqual(len(maternal_identifier.infants), 3)

    def test_update_identifiermodel(self):
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        maternal_identifier.deliver(3, model='edc_identifier.maternallabdel')
        self.assertEqual(len(maternal_identifier.infants), 3)
        self.assertEqual(IdentifierModel.objects.filter(
            name='infantidentifier').count(), 3)
        self.assertEqual(
            IdentifierModel.objects.filter(
                subject_type='infant',
                model='edc_identifier.maternallabdel',
                protocol_number='000',
                study_site='40').count(), 3)

    def test_load_maternal_identifier_and_singleton(self):
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
        maternal_identifier.deliver(1, model='edc_identifier.maternallabdel')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-10')

    def test_load_maternal_identifier_and_twins(self):
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        maternal_identifier.deliver(2, model='edc_identifier.maternallabdel')
        maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-25')
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-26')

    def test_load_maternal_identifier_and_twins_2nd_registered(self):
        maternal_identifier = MaternalIdentifier(
            identifier_type='subject',
            model='edc_identifier.enrollment',
            protocol_number='000',
            device_id='99',
            site_code='40',
            last_name=fake.last_name(),
            create_registration=True)
        maternal_identifier.deliver(
            2, model='edc_identifier.maternallabdel', birth_orders='2')
        maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
        self.assertEqual(maternal_identifier.infants[0].identifier, None)
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-26')

    def test_creates_registered_subject(self):
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
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
        maternal_identifier.deliver(1, model='edc_identifier.maternallabdel')
        try:
            RegisteredSubject.objects.get(
                subject_identifier='000-40990001-6-10')
        except RegisteredSubject.DoesNotExist:
            self.fail('RegisteredSubject.DoesNotExist unexpectedly raised')

    def test_does_not_create_registered_subject(self):
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
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
        maternal_identifier.deliver(
            1, model='edc_identifier.maternallabdel', create_registration=False)
        try:
            RegisteredSubject.objects.get(
                subject_identifier='000-40990001-6-10')
            self.fail('RegisteredSubject.DoesNotExist unexpectedly raised')
        except RegisteredSubject.DoesNotExist:
            pass

    def test_creates_registered_subject_with_user_created(self):
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
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
        maternal_identifier.deliver(
            1, model='edc_identifier.maternallabdel', create_registration=True)
        obj = RegisteredSubject.objects.get(
            subject_identifier='000-40990001-6-10')
        self.assertIsNotNone(obj.user_created)
