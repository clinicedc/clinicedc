from faker import Faker

from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_protocol.exceptions import SubjectTypeCapError

from .alphanumeric_identifier import AlphanumericIdentifier
from .checkdigit_mixins import LuhnMixin, LuhnOrdMixin
from .exceptions import IdentifierError, CheckDigitError, SubjectIdentifierError
from .identifier import Identifier
from .identifier_with_checkdigit import IdentifierWithCheckdigit
from .models import IdentifierHistory, IdentifierModel
from .numeric_identifier import NumericIdentifier, NumericIdentifierWithModulus
from .short_identifier import ShortIdentifier
from .subject_identifier import SubjectIdentifier
from .maternal_identifier import MaternalIdentifier


fake = Faker()


class TestIdentifierError(Exception):
    pass


@tag('maternal')
class TestMaternalIdentifier(TestCase):

    def test_create(self):
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name())
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')

    def test_creates_registered_subject(self):
        RegisteredSubject = django_apps.get_app_config(
            'edc_registration').model
        MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        try:
            RegisteredSubject.objects.get(subject_identifier='000-40990001-6')
        except RegisteredSubject.DoesNotExist:
            self.fail('RegisteredSubject.DoesNotExist unexpectedly raised')

    def test_creates_registered_subject_attrs(self):
        RegisteredSubject = django_apps.get_app_config(
            'edc_registration').model
        MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        obj = RegisteredSubject.objects.get(
            subject_identifier='000-40990001-6')
        self.assertEqual(obj.study_site, '40')
        self.assertEqual(obj.subject_type, 'subject')
        self.assertIsNotNone(obj.last_name)


@tag('infant')
class TestInfantIdentifier(TestCase):

    def test_create_singleton(self):
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(1, model='edc_example.maternallabdel')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-10')

    def test_create_twins(self):
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(2, model='edc_example.maternallabdel')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-25')
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-26')

    def test_create_triplets(self):
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(3, model='edc_example.maternallabdel')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-36')
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-37')
        self.assertEqual(
            maternal_identifier.infants[2].identifier, '000-40990001-6-38')

    def test_create_triplets_only_registered_2nd_born_as_list(self):
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(
            3, model='edc_example.maternallabdel', birth_orders=[2])
        self.assertEqual(maternal_identifier.infants[0].identifier, None)
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-37')
        self.assertEqual(maternal_identifier.infants[2].identifier, None)
        self.assertEqual(len(maternal_identifier.infants), 3)

    def test_create_triplets_only_registered_2nd_born(self):
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(
            3, model='edc_example.maternallabdel', birth_orders='2')
        self.assertEqual(maternal_identifier.infants[0].identifier, None)
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-37')
        self.assertEqual(maternal_identifier.infants[2].identifier, None)
        self.assertEqual(len(maternal_identifier.infants), 3)

    def test_create_triplets_only_registered_1st_born(self):
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(
            3, model='edc_example.maternallabdel', birth_orders='1')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-36')
        self.assertEqual(maternal_identifier.infants[1].identifier, None)
        self.assertEqual(maternal_identifier.infants[2].identifier, None)
        self.assertEqual(len(maternal_identifier.infants), 3)

    def test_create_triplets_only_registered_all_explicitly(self):
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(
            3, model='edc_example.maternallabdel', birth_orders='1,2,3')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-36')
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-37')
        self.assertEqual(
            maternal_identifier.infants[2].identifier, '000-40990001-6-38')
        self.assertEqual(len(maternal_identifier.infants), 3)

    def test_create_triplets_only_registered_all_by_default(self):
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier.deliver(
            3, model='edc_example.maternallabdel', birth_orders=None)
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-36')
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-37')
        self.assertEqual(
            maternal_identifier.infants[2].identifier, '000-40990001-6-38')
        self.assertEqual(len(maternal_identifier.infants), 3)

    def test_update_identifiermodel(self):
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        maternal_identifier.deliver(3, model='edc_example.maternallabdel')
        self.assertEqual(len(maternal_identifier.infants), 3)
        self.assertEqual(IdentifierModel.objects.filter(
            name='infantidentifier').count(), 3)
        self.assertEqual(
            IdentifierModel.objects.filter(
                subject_type='infant',
                model='edc_example.maternallabdel',
                protocol_number='000',
                study_site='40').count(), 3)

    def test_load_maternal_identifier_and_singleton(self):
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
        maternal_identifier.deliver(1, model='edc_example.maternallabdel')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-10')

    def test_load_maternal_identifier_and_twins(self):
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        maternal_identifier.deliver(2, model='edc_example.maternallabdel')
        maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
        self.assertEqual(
            maternal_identifier.infants[0].identifier, '000-40990001-6-25')
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-26')

    def test_load_maternal_identifier_and_twins_2nd_registered(self):
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        maternal_identifier.deliver(
            2, model='edc_example.maternallabdel', birth_orders='2')
        maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
        self.assertEqual(maternal_identifier.infants[0].identifier, None)
        self.assertEqual(
            maternal_identifier.infants[1].identifier, '000-40990001-6-26')

    def test_creates_registered_subject(self):
        RegisteredSubject = django_apps.get_app_config(
            'edc_registration').model
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
        maternal_identifier.deliver(1, model='edc_example.maternallabdel')
        try:
            RegisteredSubject.objects.get(
                subject_identifier='000-40990001-6-10')
        except RegisteredSubject.DoesNotExist:
            self.fail('RegisteredSubject.DoesNotExist unexpectedly raised')

    def test_does_not_create_registered_subject(self):
        RegisteredSubject = django_apps.get_app_config(
            'edc_registration').model
        maternal_identifier = MaternalIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
        maternal_identifier.deliver(
            1, model='edc_example.maternallabdel', create_registration=False)
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
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40',
            last_name=fake.last_name(),
            create_registration=True)
        self.assertEqual(maternal_identifier.identifier, '000-40990001-6')
        maternal_identifier = MaternalIdentifier(identifier='000-40990001-6')
        maternal_identifier.deliver(
            1, model='edc_example.maternallabdel', create_registration=True)
        obj = RegisteredSubject.objects.get(
            subject_identifier='000-40990001-6-10')
        self.assertIsNotNone(obj.user_created)


@tag('subject')
class TestSubjectIdentifier(TestCase):

    def test_raises_on_unknown_cap(self):
        """Asserts raises exception if cannot find cap."""
        try:
            SubjectIdentifier(
                subject_type_name='subject',
                model='edc_example.enrollment',
                protocol='000',
                device_id='99',
                study_site='40')
        except SubjectTypeCapError:
            self.fail('SubjectTypeCapError unexpectedly raised')
        self.assertRaises(
            SubjectTypeCapError,
            SubjectIdentifier,
            subject_type_name='subject',
            model='edc_example.enrollmentblahblahblah',
            protocol='000',
            device_id='99',
            study_site='40')

    def test_increments(self):
        """Asserts identifier sequence increments correctly."""
        subject_type_name = 'subject'
        model_name = 'edc_example.enrollment'
        study_site = '40'
        app_config = django_apps.get_app_config('edc_protocol')
        cap = app_config.get_cap(subject_type_name, model_name, study_site)
        padding = len(str(cap.max_subjects))
        for i in range(1, 10):
            subject_identifier = SubjectIdentifier(
                subject_type_name=subject_type_name,
                model=model_name,
                study_site=study_site,
                padding=padding)
            self.assertEqual(
                subject_identifier.identifier[8:12], '000' + str(i))

    def test_create_missing_args(self):
        """Asserts raises exception for missing subject_type_name."""
        self.assertRaises(
            SubjectTypeCapError,
            SubjectIdentifier,
            subject_type_name='',
            model='edc_example.enrollment',
            study_site='40')

    def test_create_missing_args2(self):
        """Asserts raises exception for missing model."""
        self.assertRaises(
            SubjectTypeCapError,
            SubjectIdentifier,
            subject_type_name='subject',
            model='',
            study_site='40')

    def test_create_missing_args3(self):
        """Asserts raises exception for missing study_site."""
        self.assertRaises(
            SubjectIdentifierError,
            SubjectIdentifier,
            subject_type_name='subject',
            model='edc_example.enrollment',
            study_site='')

    def test_create1(self):
        """Asserts exact first identifier given parameters."""
        subject_identifier = SubjectIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            protocol='000',
            device_id='99',
            study_site='40')
        self.assertEqual('000-40990001-6', subject_identifier.identifier)

    def test_create2(self):
        """Asserts exact first identifier required parameters and those fetched from edc-example.AppConfig."""
        subject_identifier = SubjectIdentifier(
            subject_type_name='subject',
            model='edc_example.enrollment',
            study_site='40')
        self.assertEqual('000-40140001-5', subject_identifier.identifier)

    def test_create_hits_cap(self):
        """Asserts raises exception if attempt to exceed cap."""
        for _ in range(1, 6):
            SubjectIdentifier(
                subject_type_name='subject',
                model='edc_example.enrollmentthree',
                protocol='000',
                device_id='99',
                study_site='40')
        self.assertEqual(IdentifierModel.objects.all().count(), 5)
        self.assertRaises(
            SubjectTypeCapError,
            SubjectIdentifier,
            subject_type_name='subject',
            model='edc_example.enrollmentthree',
            protocol='000',
            device_id='99',
            study_site='40')

    def test_create_hits_cap_with_other_models(self):
        """Asserts raises exception if attempt to exceed cap."""
        for _ in range(0, 10):
            SubjectIdentifier(
                subject_type_name='subject',
                model='edc_example.enrollment',
                protocol='000',
                device_id='99',
                study_site='40')
        for _ in range(0, 5):
            SubjectIdentifier(
                subject_type_name='subject',
                model='edc_example.enrollmentthree',
                protocol='000',
                device_id='99',
                study_site='40')
        self.assertEqual(IdentifierModel.objects.filter(
            model='edc_example.enrollmentthree').count(), 5)
        self.assertRaises(
            SubjectTypeCapError,
            SubjectIdentifier,
            subject_type_name='subject',
            model='edc_example.enrollmentthree',
            protocol='000',
            device_id='99',
            study_site='40')

    def test_updates_identifier_model(self):
        """Asserts updates Identifier model with all attributes."""
        for _ in range(0, 5):
            SubjectIdentifier(
                subject_type_name='subject',
                model='edc_example.enrollmentthree',
                protocol='000',
                device_id='99',
                study_site='40')
        self.assertEqual(IdentifierModel.objects.all().count(), 5)
        self.assertEqual(
            IdentifierModel.objects.filter(
                subject_type='subject',
                model='edc_example.enrollmentthree',
                protocol_number='000',
                device_id='99',
                study_site='40').count(), 5)


class TestIdentifier(TestCase):

    def test_valid_checkdigit(self):
        mixin = LuhnMixin()
        checkdigit = mixin.calculate_checkdigit('98765')
        self.assertTrue(mixin.is_valid_checkdigit('98765', checkdigit))
        checkdigit = mixin.calculate_checkdigit('98766')
        self.assertTrue(mixin.is_valid_checkdigit('98766', checkdigit))
        checkdigit = mixin.calculate_checkdigit('98767')
        self.assertTrue(mixin.is_valid_checkdigit('98767', checkdigit))

    def test_luhn_mixin(self):
        mixin = LuhnMixin()
        self.assertEqual('1', mixin.calculate_checkdigit('98765'))
        self.assertEqual('9', mixin.calculate_checkdigit('98766'))
        self.assertEqual('7', mixin.calculate_checkdigit('98767'))

    def test_luhn_ord_mixin(self):
        mixin = LuhnOrdMixin()
        self.assertEqual('4', mixin.calculate_checkdigit('ABCDE'))
        self.assertEqual('8', mixin.calculate_checkdigit('ABCDEF'))
        self.assertEqual('0', mixin.calculate_checkdigit('ABCDEFG'))

    def test_identifier(self):
        instance = Identifier()
        self.assertEqual('1', instance.identifier)
        instance = Identifier()
        self.assertEqual('2', instance.identifier)

    def test_identifier_with_checkdigit(self):
        instance = IdentifierWithCheckdigit()
        self.assertEqual('18', instance.identifier)
        instance = IdentifierWithCheckdigit()
        self.assertEqual('26', instance.identifier)
        instance = IdentifierWithCheckdigit()
        self.assertEqual('34', instance.identifier)

    def test_short_identifier(self):
        ShortIdentifier.prefix_pattern = '^[0-9]{2}$'
        short_identifier = ShortIdentifier(options=dict(prefix=22))
        expected_identifier = '{}{}'.format(
            '22', short_identifier.options.get('random_string'))
        self.assertEqual(short_identifier.identifier, expected_identifier)
        self.assertIsInstance(
            IdentifierHistory.objects.get(identifier=expected_identifier),
            IdentifierHistory
        )
        self.assertIsInstance(
            IdentifierHistory.objects.get(
                identifier=short_identifier.identifier),
            IdentifierHistory
        )
        self.assertIsNotNone(short_identifier.identifier)
        ShortIdentifier.prefix_pattern = None

    def test_short_identifier_with_last(self):
        ShortIdentifier.prefix_pattern = '^[0-9]{2}$'
        ShortIdentifier.checkdigit_pattern = None
        ShortIdentifier.history_model.objects.create(
            identifier='22KVTB4',
            identifier_type=ShortIdentifier.name,
            identifier_prefix='22')
        short_identifier = ShortIdentifier(options={'prefix': 22})
        expected_identifier = '{}{}'.format(
            '22', short_identifier.options.get('random_string'))
        self.assertEqual(short_identifier.identifier, expected_identifier)
        self.assertNotEqual(short_identifier.identifier, '22KVTB4')
        self.assertIsInstance(
            IdentifierHistory.objects.get(identifier=expected_identifier),
            IdentifierHistory
        )
        self.assertIsInstance(
            IdentifierHistory.objects.get(
                identifier=short_identifier.identifier),
            IdentifierHistory
        )
        self.assertIsNotNone(short_identifier.identifier)
        ShortIdentifier.prefix_pattern = None

    def test_short_identifier_catches_duplicate_limit(self):
        ntries = 0
        ShortIdentifier.identifier_pattern = '^\w+$'
        ShortIdentifier.allowed_chars = 'AB'
        instance = ShortIdentifier()
        min_tries = instance.duplicate_tries
        max_tries = min_tries + 10
        assert_msg = None
        while ntries <= max_tries:
            ntries += 1
            try:
                instance = ShortIdentifier()
            except IdentifierError as e:
                assert_msg = (
                    'No available identifiers on {}th attempt. Limit is {}. Got {}'.format(
                        ntries, min_tries, str(e)))
                break
        self.assertTrue(ntries <= min_tries, assert_msg)

    def test_numeric_basic(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{8}$'
        NumericIdentifier.seed = ('10000000')
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '100000017')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '100000025')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '100000033')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '100000041')

    def test_numeric_without_checkdigit(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{8}$'
        NumericIdentifier.seed = ('10000000')
        NumericIdentifier.checkdigit_pattern = None
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '10000001')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '10000002')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '10000003')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '10000004')

    def test_numeric_without_checkdigit_last(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{8}$'
        NumericIdentifier.seed = ('10000000')
        NumericIdentifier.checkdigit_pattern = None
        numeric_identifier = NumericIdentifier(last_identifier='10000004')
        self.assertEqual(numeric_identifier.identifier, '10000005')

    def test_numeric_without_checkdigit_history(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{8}$'
        NumericIdentifier.seed = ('10000000')
        NumericIdentifier.checkdigit_pattern = None
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '10000001')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '10000002')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '10000003')
        numeric_identifier.next_identifier()
        self.assertEqual(numeric_identifier.identifier, '10000004')
        numeric_identifier = NumericIdentifier()
        self.assertEqual(numeric_identifier.identifier, '10000005')

    def test_numeric_pattern(self):
        NumericIdentifier.identifier_pattern = r'^[0-9]{10}\-[0-9]{1}$'
        NumericIdentifier.seed = ('1000000008')
        self.assertRaises(IdentifierError, NumericIdentifier, None)

    def test_numeric_seed(self):
        NumericIdentifier.separator = None
        NumericIdentifier.identifier_pattern = r'^[0-9]{10}$'
        NumericIdentifier.seed = ('1999999996')
        instance = NumericIdentifier(None)
        self.assertEqual(instance.identifier, '19999999972')
        instance.next_identifier()
        self.assertEqual(instance.identifier, '19999999980')
        instance.next_identifier()
        self.assertEqual(instance.identifier, '19999999998')
        instance.next_identifier()
        self.assertEqual(instance.identifier, '20000000008')

    def test_numeric_with_last(self):
        NumericIdentifier.separator = None
        NumericIdentifier.identifier_pattern = r'^[0-9]{9}$'
        NumericIdentifier.checkdigit_pattern = r'^[0-9]{1}$'
        NumericIdentifier.seed = ('100000008')
        instance = NumericIdentifier(last_identifier='1999999996')
        self.assertEqual(instance.identifier, '2000000006')

    def test_numeric_separator(self):
        NumericIdentifier.separator = '-'
        NumericIdentifier.identifier_pattern = r'^[0-9]{4}\-[0-9]{4}$'
        NumericIdentifier.checkdigit_pattern = r'^\-[0-9]{1}$'
        NumericIdentifier.seed = '1000-0000'
        numeric_identifier = NumericIdentifier(None)
        self.assertEqual(numeric_identifier.identifier, '1000-0001-7')

    def test_numeric_modulus(self):
        NumericIdentifierWithModulus.separator = '-'
        NumericIdentifierWithModulus.identifier_pattern = r'^[0-9]{4}[0-9]{4}[0-9]{2}$'
        NumericIdentifierWithModulus.checkdigit_pattern = r'^\-[0-9]{2}$'
        NumericIdentifierWithModulus.seed = '1000000010'
        numeric_identifier = NumericIdentifierWithModulus(None)
        self.assertEqual(numeric_identifier.identifier, '1000000011-10')
        self.assertEqual(next(numeric_identifier), '1000000012-11')

    def test_numeric_modulus_with_separator(self):
        NumericIdentifierWithModulus.separator = '-'
        NumericIdentifierWithModulus.identifier_pattern = r'^[0-9]{4}\-[0-9]{4}$'
        NumericIdentifierWithModulus.checkdigit_pattern = r'^\-[0-9]{2}$'
        NumericIdentifierWithModulus.seed = '1000-0000'
        numeric_identifier = NumericIdentifierWithModulus(None)
        self.assertEqual(numeric_identifier.identifier, '1000-0001-11')
        self.assertEqual(next(numeric_identifier), '1000-0002-12')

    def test_split_checkdigit_one(self):
        """Asserts can split identifier with checkdigit into identifier, checkdigit."""
        class DummyIdentifierWithCheckdigit(IdentifierWithCheckdigit):
            def calculate_checkdigit(self, identifier):
                return '1'

        identifier_with_checkdigit = '987651'
        instance = IdentifierWithCheckdigit()
        identifier = instance.remove_checkdigit(identifier_with_checkdigit)
        checkdigit = identifier_with_checkdigit.replace(identifier, '')
        self.assertEqual(identifier, identifier_with_checkdigit[:-1])
        self.assertEqual(checkdigit, identifier_with_checkdigit[-1:])

    def test_split_checkdigit_two(self):
        """Asserts can split identifier with checkdigit into identifier, checkdigit.

        Tries with a different the checkdigit_pattern"""
        class DummyIdentifierWithCheckdigit(IdentifierWithCheckdigit):
            checkdigit_pattern = r'^[0-9]{2}$'

            def calculate_checkdigit(self, identifier):
                return '51'

        instance = DummyIdentifierWithCheckdigit()
        identifier_with_checkdigit = '987651'
        identifier = instance.remove_checkdigit(identifier_with_checkdigit)
        checkdigit = identifier_with_checkdigit.replace(identifier, '')
        self.assertEqual(identifier, identifier_with_checkdigit[:-2])
        self.assertEqual(checkdigit, identifier_with_checkdigit[-2:])

    def test_split_checkdigit_exception(self):
        """Asserts raises an exception if cannot split based on the pattern and identifier.

        Note, checkdigit_pattern does not match"""
        class DummyIdentifierWithCheckDigit(IdentifierWithCheckdigit):

            checkdigit_pattern = r'^[0-9]{2}$'

            def calculate_checkdigit(self, identifier):
                return '54'

        instance = DummyIdentifierWithCheckDigit()
        identifier_with_checkdigit = '98765-4'
        self.assertRaises(
            CheckDigitError, instance.remove_checkdigit, identifier_with_checkdigit)

    def test_checkdigit(self):
        identifier = 'AAA00007'
        alpha_identifier = AlphanumericIdentifier(identifier)
        identifier_with_checkdigit = alpha_identifier.identifier
        identifier = alpha_identifier.remove_checkdigit(
            identifier_with_checkdigit)
        checkdigit = identifier_with_checkdigit.replace(identifier, '')
        self.assertEqual(checkdigit, '5')
        self.assertEqual(identifier_with_checkdigit, 'AAA00015')
        alpha_identifier.next()
        self.assertEqual(alpha_identifier.identifier, 'AAA00023')
        alpha_identifier.next()
        self.assertEqual(alpha_identifier.identifier, 'AAA00031')

    def test_alphanumeric(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ['AAA', '0000']
        alpha_id = AlphanumericIdentifier(None)
        self.assertEqual(alpha_id.identifier, 'AAA00015')
        self.assertEqual(next(alpha_id), 'AAA00023')
        self.assertEqual(next(alpha_id), 'AAA00031')
        self.assertEqual(next(alpha_id), 'AAA00049')
        self.assertEqual(next(alpha_id), 'AAA00057')
        self.assertEqual(next(alpha_id), 'AAA00065')

    def test_alphanumeric_last(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ['AAA', '0000']
        alpha_id = AlphanumericIdentifier('AAA99991')
        self.assertEqual(next(alpha_id), 'AAB00021')
        self.assertEqual(next(alpha_id), 'AAB00039')
        self.assertEqual(next(alpha_id), 'AAB00047')
        self.assertEqual(next(alpha_id), 'AAB00055')

    def test_increment_for_alphanumeric(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ['AAA', '0000']
        instance = AlphanumericIdentifier(None)
        self.assertEquals(instance.identifier, 'AAA00015')
        for n in range(10000):
            identifier = next(instance)
            if n >= 9998:
                self.assertEqual('AAB', identifier[0:3])
            else:
                self.assertEqual('AAA', identifier[0:3],
                                 'Expected AAA for {}nth iteration. Got {}'.format(n, identifier))

    def test_alphanumeric_with_prefix(self):
        AlphanumericIdentifier.alpha_pattern = r'^[A-Z]{3}$'
        AlphanumericIdentifier.numeric_pattern = r'^[0-9]{4}$'
        AlphanumericIdentifier.seed = ['AAA', '0000']
        instance = AlphanumericIdentifier(prefix='ERIK')
        self.assertTrue(instance.identifier.startswith('ERIK'))
