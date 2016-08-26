import factory

from faker import Factory as FakerFactory

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.forms import ModelForm
from django.test.testcases import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from django.utils.six import StringIO

from edc_consent.exceptions import NotConsentedError, SiteConsentError, ConsentVersionError
from edc_consent.models.validators import AgeTodayValidator

from edc_consent.exceptions import AlreadyRegistered
from edc_consent.site_consents import site_consents
from edc_constants.constants import YES, NO
from edc_consent.consent import Consent

from edc_example.factories import SubjectConsentFactory, SubjectConsentProxy, SubjectConsentProxyFactory
from edc_example.models import SubjectConsent, SubjectConsentProxy, SubjectVisit, CrfOne, Enrollment, Appointment

from .form_mixins import ConsentFormMixin
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

faker = FakerFactory.create()
app_config = django_apps.get_app_config('edc_consent')


def consent_factory(**kwargs):
    options = dict(
        app_label=kwargs.get('app_label', 'edc_example'),
        model_name=kwargs.get('model_name', 'subjectconsent'),
        start=kwargs.get('start', timezone.now() - timedelta(days=365)),
        end=kwargs.get('end', timezone.now() + timedelta(days=365)),
        version=kwargs.get('version', '1'),
        updates_version=kwargs.get('updates_version', ''),
    )
    model = '{}.{}'.format(kwargs.get('app_label', 'edc_example'), kwargs.get('model_name', 'subjectconsent'))
    consent = Consent(model, **options)
    site_consents.register(consent)
    return consent

faker = FakerFactory.create()


class SubjectConsentForm(ConsentFormMixin, ModelForm):

    class Meta:
        model = SubjectConsent
        fields = '__all__'


class SubjectConsentProxyForm(ConsentFormMixin, ModelForm):

    class Meta:
        model = SubjectConsentProxy
        fields = '__all__'


class TestConsent(TestCase):

    def setUp(self):
        site_consents.reset_registry()

    def test_raises_error_if_no_consent(self):
        """Asserts SubjectConsent cannot create a new instance if no consents are defined.
        (note: site_consents.reset_registry called in setUp) """
        subject_identifier = '12345'
        self.assertRaises(SiteConsentError, SubjectConsentFactory, subject_identifier=subject_identifier)

    def test_raises_error_if_no_consent2(self):
        """Asserts a model using the RequiresConsentMixin cannot create a new instance if subject
        not consented."""
        consent_factory()
        RegisteredSubject = django_apps.get_app_config('edc_registration').model
        RegisteredSubject.objects.create(subject_identifier='12345')
        self.assertRaises(NotConsentedError, Enrollment.objects.create, subject_identifier='12345')

    def test_allows_create_if_consent(self):
        consent_factory()
        subject_identifier = '12345'
        SubjectConsentFactory(subject_identifier=subject_identifier)
        Enrollment.objects.create(subject_identifier=subject_identifier)
        self.assertEqual(Appointment.objects.all().count(), 4)

    def test_cannot_create_consent_without_consent_by_datetime(self):
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() - timedelta(days=200),
            version='1.0')
        self.assertRaises(SiteConsentError, SubjectConsentFactory)

    def test_consent_gets_version(self):
        consent_factory(version='1.0')
        consent = SubjectConsentFactory()
        self.assertEqual(consent.version, '1.0')

    def test_model_gets_version(self):
        consent = consent_factory(version='1.0')
        subject_identifier = '12345'
        SubjectConsentFactory(subject_identifier=subject_identifier)
        enrollment = Enrollment.objects.create(subject_identifier=subject_identifier)
        self.assertEqual(enrollment.consent_version, '1.0')

    def test_model_consent_version_no_change(self):
        consent_factory(version='1.2')
        subject_identifier = '12345'
        SubjectConsentFactory(subject_identifier=subject_identifier)
        enrollment = Enrollment.objects.create(subject_identifier=subject_identifier)
        self.assertEqual(enrollment.consent_version, '1.2')
        enrollment.save()
        self.assertEqual(enrollment.consent_version, '1.2')

    def test_model_consent_version_changes_with_report_datetime(self):
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() - timedelta(days=200),
            version='1.0')
        consent_factory(
            start=timezone.now() - timedelta(days=199),
            end=timezone.now() + timedelta(days=100),
            version='1.1')
        subject_identifier = '12345'
        SubjectConsentFactory(
            subject_identifier=subject_identifier,
            consent_datetime=timezone.now() - timedelta(days=300))
        enrollment = Enrollment.objects.create(
            subject_identifier=subject_identifier,
            report_datetime=timezone.now() - timedelta(days=300))
        self.assertEqual(enrollment.consent_version, '1.0')
        SubjectConsentFactory(subject_identifier=subject_identifier)
        enrollment.report_datetime = timezone.now()
        enrollment.save()
        self.assertEqual(enrollment.consent_version, '1.1')

    def test_consent_update_needs_previous_version(self):
        """Asserts that a consent type updates a previous consent."""
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() - timedelta(days=200),
            version='1.0')
        self.assertRaises(
            SiteConsentError, consent_factory,
            start=timezone.now() - timedelta(days=199),
            end=timezone.now() + timedelta(days=100),
            version='1.1',
            updates_version='1.2')
        consent_factory(
            start=timezone.now() - timedelta(days=199),
            end=timezone.now() - timedelta(days=100),
            version='1.1',
            updates_version='1.0')

    def test_consent_needs_previous_version(self):
        """Asserts that a consent updates a previous consent but cannot be entered by itself."""
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() - timedelta(days=200),
            version='1.0')
        consent_factory(
            start=timezone.now() - timedelta(days=199),
            end=timezone.now() + timedelta(days=200),
            version='1.1',
            updates_version='1.0')
        self.assertRaises(ConsentVersionError, SubjectConsentFactory)

    def test_consent_needs_previous_version2(self):
        """Asserts that a consent updates a previous consent but cannot be entered by itself."""
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() - timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory(consent_datetime=timezone.now() - timedelta(days=300))
        self.assertEqual(consent.version, '1.0')
        consent_factory(
            start=timezone.now() - timedelta(days=199),
            end=timezone.now() + timedelta(days=200),
            version='1.1',
            updates_version='1.0')
        consent = SubjectConsentFactory(
            first_name=consent.first_name,
            last_name=consent.last_name,
            initials=consent.initials)
        self.assertEqual(consent.version, '1.1')

    def test_consent_needs_previous_version3(self):
        """Asserts that a consent updates a previous consent but cannot be entered by itself."""
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() - timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory(consent_datetime=timezone.now() - timedelta(days=300))
        self.assertEqual(consent.version, '1.0')
        consent_factory(
            start=timezone.now() - timedelta(days=199),
            end=timezone.now() - timedelta(days=50),
            version='1.1',
            updates_version='1.0')
        consent_factory(
            start=timezone.now() - timedelta(days=49),
            end=timezone.now() + timedelta(days=200),
            version='1.2',
            updates_version='1.1')
        self.assertRaises(ConsentVersionError, SubjectConsentFactory)

    def test_consent_periods_cannot_overlap(self):
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() - timedelta(days=200),
            version='1.0')
        self.assertRaises(
            AlreadyRegistered, consent_factory,
            start=timezone.now() - timedelta(days=201),
            end=timezone.now(),
            version='1.1',
            updates_version='1.0')

    def test_consent_periods_cannot_overlap2(self):
        consent_factory(
            app_label='example',
            model_name='testconsentmodel',
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        self.assertRaises(
            AlreadyRegistered, consent_factory,
            app_label='example',
            model_name='testconsentmodel',
            start=timezone.now() - timedelta(days=201),
            end=timezone.now() + timedelta(days=201),
            version='1.1')

    def test_encryption(self):
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory(
            first_name='ERIK',
            consent_datetime=timezone.now() - timedelta(days=300))
        self.assertEqual(consent.first_name, 'ERIK')

    def test_no_subject_identifier(self):
        """Asserts a blank subject identifier is set to the subject_identifier_as_pk."""
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory(
            subject_identifier=None, consent_datetime=timezone.now() - timedelta(days=300))
        self.assertEqual(consent.subject_identifier, consent.subject_identifier_as_pk)
        consent.subject_identifier = '12345'
        consent.save()
        self.assertEqual(consent.subject_identifier, '12345')

    def test_consent_age_validator(self):
        validator = AgeTodayValidator(16, 64)
        self.assertIsNone(validator(date.today() - relativedelta(years=25)))
        self.assertRaises(ValidationError, validator, date.today() - relativedelta(years=15))
        self.assertRaises(ValidationError, validator, date.today() - relativedelta(years=65))

    def test_subject_has_current_consent(self):
        subject_identifier = '123456789'
        identity = '987654321'
        report_datetime = timezone.now() - timedelta(days=1)
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() - timedelta(days=200),
            version='1.0')
        consent_factory(
            start=timezone.now() - timedelta(days=199),
            end=timezone.now() + timedelta(days=200),
            version='2.0')
        SubjectConsentFactory(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity,
            consent_datetime=timezone.now() - timedelta(days=300))
        self.assertIsNone(SubjectConsent.consent.valid_consent_for_period(
            '123456789', report_datetime))
        SubjectConsentFactory(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity,
            consent_datetime=report_datetime)
        self.assertIsNotNone(SubjectConsent.consent.valid_consent_for_period(
            '123456789', report_datetime))

    def test_consent_may_updates_more_than_one_version(self):
        subject_identifier = '123456789'
        identity = '987654321'
        report_datetime = timezone.now() - timedelta(days=1)
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() - timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory(
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=timezone.now() - timedelta(days=300))
        consent_factory(
            start=timezone.now() - timedelta(days=199),
            end=timezone.now() - timedelta(days=50),
            version='2.0',
            updates_version='1.0')
        consent_factory(
            start=timezone.now() - timedelta(days=49),
            end=timezone.now() + timedelta(days=200),
            version='3.0',
            updates_version='1.0,2.0')
        SubjectConsentFactory(
            first_name=consent.first_name,
            last_name=consent.last_name,
            initials=consent.initials,
            subject_identifier=subject_identifier,
            identity=identity,
            confirm_identity=identity,
            consent_datetime=report_datetime)

    def test_scheduled_model_with_fk(self):
        subject_identifier = '123456789'
        identity = '987654321'
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        SubjectConsentFactory(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity)
        Enrollment.objects.create(subject_identifier=subject_identifier)
        appointment = Appointment.objects.all().order_by('created')[0]
        subject_visit = SubjectVisit.objects.create(
            report_datetime=timezone.now(),
            appointment=appointment)
        CrfOne.objects.create(subject_visit=subject_visit)

    def test_base_form_identity_dupl(self):
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() - timedelta(days=100),
            version='1.0')
        consent_factory(
            start=timezone.now() - timedelta(days=99),
            end=timezone.now() + timedelta(days=200),
            version='2.0')
        consent1 = SubjectConsentFactory()
        consent1.save()
        consent2 = SubjectConsentFactory(
            subject_identifier='123455',
            identity='123156788', confirm_identity='123156788')
        consent2.identity = consent1.identity
        consent2.confirm_identity = consent1.confirm_identity
        consent_form = SubjectConsentForm(data=consent2.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn('Identity \'123156789\' is already in use by subject 12345', ','.join(
            consent_form.non_field_errors()))

    def test_base_form_guardian_and_dob1(self):
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory.build()
        consent.guardian_name = None
        age_is_adult = app_config.get_consent(SubjectConsent._meta.label_lower).age_is_adult
        consent.dob = timezone.now() - relativedelta(years=age_is_adult - 1)
        consent_form = SubjectConsentForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn('Subject is a minor', ','.join(consent_form.non_field_errors()))

    def test_base_form_guardian_and_dob2(self):
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory.build()
        consent.guardian_name = 'SPOCK, YOUCOULDNTPRONOUNCEIT'
        age_is_adult = app_config.get_consent(SubjectConsent._meta.label_lower).age_is_adult
        consent.dob = timezone.now() - relativedelta(years=age_is_adult)
        consent_form = SubjectConsentForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn('Subject is an adult', ','.join(consent_form.non_field_errors()))

    def test_base_form_guardian_and_dob3(self):
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory.build()
        age_is_adult = app_config.get_consent(SubjectConsent._meta.label_lower).age_is_adult
        consent.dob = timezone.now() - relativedelta(years=age_is_adult)
        consent_form = SubjectConsentForm(data=consent.__dict__)
        self.assertTrue(consent_form.is_valid())

    def test_base_form_catches_dob_lower(self):
        subject_identifier = '123456789'
        identity = '987654321'
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity,
            dob=date.today())
        consent_form = SubjectConsentForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn(
            'Subject\'s age is 0d. Subject is not eligible for consent.',
            ','.join(consent_form.non_field_errors()))

    def test_base_form_catches_dob_upper(self):
        subject_identifier = '123456789'
        identity = '987654321'
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity,
            dob=date.today() - relativedelta(years=100))
        consent_form = SubjectConsentForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn(
            'Subject\'s age is 100y. Subject is not eligible for consent.',
            ','.join(consent_form.non_field_errors()))

    def test_base_form_catches_gender_of_consent(self):
        consent_factory(
            app_label=SubjectConsentProxy._meta.app_label,
            model_name=SubjectConsentProxy._meta.model_name,
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = SubjectConsentProxyFactory.build(gender='F')
        form = SubjectConsentProxyForm(data=consent.__dict__)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Gender of consent can only be \'M\'. Got \'F\'.',
            form.errors.get('gender') or [])
        consent = SubjectConsentProxyFactory.build(gender='M')
        form = SubjectConsentProxyForm(data=consent.__dict__)
        self.assertTrue(form.is_valid())

    def test_base_form_catches_is_literate_and_witness(self):
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory(is_literate=NO)
        consent_form = SubjectConsentProxyForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn(
            'subject is illiterate',
            ','.join(consent_form.non_field_errors()))
        consent.witness_name = 'X'
        consent_form = SubjectConsentProxyForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn(
            'Format is \'LASTNAME, FIRSTNAME\'',
            ','.join(consent_form.errors.get('witness_name', [])))
        consent.witness_name = 'SPOCK, YOUCOULDNTPRONOUNCEIT'
        consent_form = SubjectConsentProxyForm(data=consent.__dict__)
        self.assertTrue(consent_form.is_valid())

    @override_settings(STUDY_OPEN_DATETIME=timezone.datetime.today() - relativedelta(years=3))
    def test_base_form_catches_consent_datetime_before_study_open(self):
        study_open_date = (timezone.datetime.today() - relativedelta(years=3)).date().isoformat()
        subject_identifier = '123456789'
        identity = '987654321'
        consent_factory(
            start=timezone.now() - relativedelta(years=5),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory.build(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity,
            consent_datetime=timezone.now() - relativedelta(years=4),
            dob=date.today() - relativedelta(years=25))
        consent_form = SubjectConsentForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        validation_message = ','.join(consent_form.errors.get('consent_datetime'))
        self.assertIn('Invalid date. Study opened on {}'.format(study_open_date),
                      validation_message)
        consent = SubjectConsentFactory.build(
            subject_identifier=subject_identifier, identity=identity, confirm_identity=identity,
            consent_datetime=timezone.now() - relativedelta(years=2),
            dob=date.today() - relativedelta(years=25))
        consent_form = SubjectConsentForm(data=consent.__dict__)
        self.assertIsNone(consent_form.errors.get('consent_datetime'))

    def test_updateconsentversion_management(self):
        out = StringIO()
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() - timedelta(days=100),
            version='1.0')
        consent_factory(
            start=timezone.now() - timedelta(days=99),
            end=timezone.now() + timedelta(days=200),
            version='2.0')
        consent2 = SubjectConsentFactory()
        consent1 = SubjectConsentFactory(
            subject_identifier='987654321',
            identity='123112345', confirm_identity='123112345',
            consent_datetime=timezone.now() - timedelta(days=150))
        consent1.version = '?'
        consent2.version = '?'
        consent1.save_base(update_fields=['version'])
        consent2.save_base(update_fields=['version'])
        consent1 = SubjectConsent.objects.get(pk=consent1.pk)
        consent2 = SubjectConsent.objects.get(pk=consent2.pk)
        self.assertEqual(consent1.version, '?')
        self.assertEqual(consent2.version, '?')
        call_command('updateconsentversion', stdout=out)
        self.assertIn('Found consents: {}'.format(SubjectConsent._meta.verbose_name), out.getvalue())
        self.assertIn("Updating {} \'{}\' where version == \'?\' ... ".format(
            2, SubjectConsent._meta.verbose_name), out.getvalue())
        consent1 = SubjectConsent.objects.get(pk=consent1.pk)
        consent2 = SubjectConsent.objects.get(pk=consent2.pk)
        self.assertEqual(consent1.version, '1.0')
        self.assertEqual(consent2.version, '2.0')

    def test_base_form_is_valid(self):
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory.build()
        consent_form = SubjectConsentForm(data=consent.__dict__)
        self.assertTrue(consent_form.is_valid())

    def test_base_form_identity_mismatch(self):
        consent_factory(
            start=timezone.now() - timedelta(days=365),
            end=timezone.now() + timedelta(days=200),
            version='1.0')
        consent = SubjectConsentFactory()
        consent.confirm_identity = '1'
        consent_form = SubjectConsentForm(data=consent.__dict__)
        self.assertFalse(consent_form.is_valid())
        self.assertIn(u'Identity mismatch', ','.join(consent_form.non_field_errors()))

