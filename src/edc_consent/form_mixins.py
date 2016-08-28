import pytz

from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.forms import ValidationError
from django.conf import settings
from django.utils.timezone import is_naive
from django.forms.utils import ErrorList

from edc_base.utils import formatted_age
from edc_constants.constants import YES, NO

from .site_consents import site_consents
from django.core.exceptions import ObjectDoesNotExist

tz = pytz.timezone(settings.TIME_ZONE)


class ConsentFormMixin:
    """Form for models that are a subclass of BaseConsent."""

    def clean(self):
        cleaned_data = super(ConsentFormMixin, self).clean()
        self.clean_gender_of_consent()
        self.clean_identity_and_confirm_identity()
        self.clean_identity_with_unique_fields()
        self.clean_initials_with_full_name()
        self.clean_dob_relative_to_consent_datetime()
        self.clean_guardian_and_dob()
        self.clean_is_literate_and_witness()
        return cleaned_data

    @property
    def consent_config(self):
        cleaned_data = self.cleaned_data
        return site_consents.get_by_datetime(
            self._meta.model._meta.label_lower,
            cleaned_data.get('consent_datetime') or self.data.get('consent_datetime')
        )

    def clean_consent_datetime(self):
        consent_datetime = self.cleaned_data['consent_datetime']
        app_config = django_apps.get_app_config('edc_protocol')
        if consent_datetime < app_config.study_open_datetime:
            self.add_error('consent_datetime', ValidationError(
                'Consent date may not be before study opening date {}. Got {}.'.format(
                    app_config.study_open_datetime.date().isoformat(),
                    consent_datetime.date().isoformat()), code='invalid'))
        return consent_datetime

    def clean_identity_and_confirm_identity(self):
        cleaned_data = self.cleaned_data
        identity = cleaned_data.get('identity')
        confirm_identity = cleaned_data.get('confirm_identity')
        if identity != confirm_identity:
            raise ValidationError(
                'Identity mismatch. Identity must match the confirmation field. '
                'Got %(identity)s != %(confirm_identity)s',
                params={'identity': identity, 'confirm_identity': confirm_identity},
                code='invalid')

    def clean_identity_with_unique_fields(self):
        cleaned_data = self.cleaned_data
        identity = cleaned_data.get('identity')
        first_name = cleaned_data.get('first_name')
        initials = cleaned_data.get('initials')
        dob = cleaned_data.get('dob')
        unique_together_form = self.unique_together_string(first_name, initials, dob)
        for consent in self._meta.model.objects.filter(identity=identity):
            unique_together_model = self.unique_together_string(consent.first_name, consent.initials, consent.dob)
            if unique_together_form != unique_together_model:
                raise ValidationError(
                    'Identity \'%(identity)s\' is already in use by subject %(subject_identifier)s. '
                    'Please resolve.',
                    params={'subject_identifier': consent.subject_identifier, 'identity': identity},
                    code='invalid')
        for consent in self._meta.model.objects.filter(first_name=first_name, initials=initials, dob=dob):
            if consent.identity != identity:
                raise ValidationError(
                    'Subject\'s identity was previously reported as \'%(existing_identity)s\'. '
                    'You wrote \'%(identity)s\'. Please resolve.',
                    params={'existing_identity': consent.identity, 'identity': identity},
                    code='invalid')

    def clean_initials_with_full_name(self):
        cleaned_data = self.cleaned_data
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        initials = cleaned_data.get("initials")
        try:
            if initials[:1] != first_name[:1] or initials[-1:] != last_name[:1]:
                raise ValidationError(
                    'Initials do not match fullname. Got %(initials)s for %(first_name)s %(last_name)s',
                    params={'initials': initials, 'first_name': first_name, 'last_name': last_name},
                    code='invalid')
        except (IndexError, TypeError):
            raise ValidationError('Initials do not match fullname.')

    def clean_guardian_and_dob(self):
        """Validates if guardian is required based in AGE_IS_ADULT set on the model."""
        cleaned_data = self.cleaned_data
        guardian = cleaned_data.get("guardian_name")
        dob = cleaned_data.get('dob')
        consent_datetime = cleaned_data.get('consent_datetime', self.instance.consent_datetime)
        if is_naive(consent_datetime):
            consent_datetime = tz.localize(consent_datetime)
        rdelta = relativedelta(consent_datetime.date(), dob)
        if rdelta.years < self.consent_config.age_is_adult:
            if not guardian:
                raise ValidationError(
                    'Subject\'s age is %(age)s. Subject is a minor. Guardian\'s '
                    'name is required with signature on the paper document.',
                    params={'age': formatted_age(dob, consent_datetime.date())},
                    code='invalid')
        if rdelta.years >= self.consent_config.age_is_adult and guardian:
            if guardian:
                raise ValidationError(
                    'Subject\'s age is %(age)s. Subject is an adult. Guardian\'s name is NOT required.',
                    params={'age': formatted_age(dob, consent_datetime.date())},
                    code='invalid')

    def clean_dob_relative_to_consent_datetime(self):
        """Validates that the dob is within the bounds of MIN and MAX set on the model."""
        cleaned_data = self.cleaned_data
        dob = cleaned_data.get('dob')
        consent_datetime = cleaned_data.get('consent_datetime', self.instance.consent_datetime)
        if not consent_datetime:
            self._errors["consent_datetime"] = ErrorList(
                [u"This field is required. Please fill consent date and time."])
            raise ValidationError('Please correct the errors below.')

        if is_naive(consent_datetime):
            consent_datetime = tz.localize(consent_datetime)
        rdelta = relativedelta(consent_datetime.date(), dob)
        if rdelta.years > self.consent_config.age_max:
            raise ValidationError(
                'Subject\'s age is %(age)s. Subject is not eligible for consent. Maximum age of consent is %(max)s.',
                params={
                    'age': formatted_age(dob, consent_datetime.date()),
                    'max': self.consent_config.age_max},
                code='invalid')
        if rdelta.years < self.consent_config.age_min:
            raise ValidationError(
                'Subject\'s age is %(age)s. Subject is not eligible for consent. Minimum age of consent is %(min)s.',
                params={
                    'age': formatted_age(dob, consent_datetime.date()),
                    'min': self.consent_config.age_min},
                code='invalid')

    def clean_is_literate_and_witness(self):
        cleaned_data = self.cleaned_data
        is_literate = cleaned_data.get('is_literate')
        witness_name = cleaned_data.get('witness_name')
        if is_literate == NO and not witness_name:
            raise ValidationError(
                'You wrote subject is illiterate. Please provide the name of a witness '
                'on this form and signature on the paper document.',
                code='invalid')
        if is_literate == YES and witness_name:
            raise ValidationError(
                'You wrote subject is literate. The name of a witness is NOT required.',
                code='invalid')
        return is_literate

    def clean_consent_reviewed(self):
        consent_reviewed = self.cleaned_data.get('consent_reviewed')
        if consent_reviewed != YES:
            raise ValidationError(
                'Consent has not been reviewed with the Subject.',
                code='invalid')
        return consent_reviewed

    def clean_study_questions(self):
        study_questions = self.cleaned_data.get('study_questions')
        if study_questions != YES:
            raise ValidationError(
                'Subject\'s questions related to the consent have not been answer or discussed.',
                code='invalid')
        return study_questions

    def clean_assessment_score(self):
        assessment_score = self.cleaned_data.get('assessment_score')
        if assessment_score != YES:
            raise ValidationError(
                'The scored assessment of the subject\'s understanding of the consent '
                'should at least be passing.',
                code='invalid')
        return assessment_score

    def clean_consent_copy(self):
        consent_copy = self.cleaned_data.get('consent_copy')
        if consent_copy == NO:
            raise ValidationError(
                'The subject has not been given a copy of the consent.',
                code='invalid')
        return consent_copy

    def clean_consent_signature(self):
        consent_signature = self.cleaned_data.get('consent_signature')
        if consent_signature != YES:
            raise ValidationError(
                'The subject has not signed the consent.',
                code='invalid')
        return consent_signature

    def clean_gender_of_consent(self):
        """Validates gender is a gender of consent."""
        gender = self.cleaned_data.get("gender")
        if gender not in self.consent_config.gender:
            raise ValidationError(
                'Gender of consent can only be \'%(gender_of_consent)s\'. Got \'%(gender)s\'.',
                params={'gender_of_consent': '\' or \''.join(self.consent_config.gender), 'gender': gender},
                code='invalid')
        return gender

    def clean_dob(self):
        dob = self.cleaned_data['dob']
        if not dob:
            raise ValidationError('Date of birth is required')
        return dob

    def unique_together_string(self, first_name, initials, dob):
        try:
            dob = dob.isoforma()
        except AttributeError:
            dob = ''
        return '{}{}{}'.format(first_name, dob, initials)


class RequiresConsentFormMixin:

    def clean(self):
        cleaned_data = super(RequiresConsentFormMixin, self).clean()
        self.validate_against_consent()
        return cleaned_data

    def validate_against_consent(self):
        """Raise an exception if the report datetime doesn't make sense relative to the consent."""
        cleaned_data = self.cleaned_data
        appointment = cleaned_data.get('appointment')
        consent = self.get_consent(appointment.subject_identifier, cleaned_data.get("report_datetime"))
        if cleaned_data.get("report_datetime") < consent.consent_datetime:
            raise ValidationError("Report datetime cannot be before consent datetime")
        if cleaned_data.get("report_datetime").date() < consent.dob:
            raise ValidationError("Report datetime cannot be before DOB")

    def get_consent(self, subject_identifier, report_datetime):
        """Return an instance of the consent model."""
        consent_config = site_consents.get_by_datetime(
            self._meta.model._meta.consent_model,
            report_datetime, exception_cls=ValidationError)
        try:
            consent = consent_config.model.objects.get(
                subject_identifier=subject_identifier)
        except consent_config.model.MultipleObjectsReturned:
            consent = consent_config.model.objects.filter(
                subject_identifier=subject_identifier).order_by('version').first()
        except ObjectDoesNotExist:
            raise ValidationError(
                '\'{}\' does not exist for subject.'.format(consent_config.model._meta.verbose_name))
        return consent
