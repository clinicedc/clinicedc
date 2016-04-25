import pytz

from dateutil.relativedelta import relativedelta

from django.forms import ModelForm, ValidationError
from django.conf import settings
from django.utils.timezone import is_naive
from django.forms.util import ErrorList

from edc_constants.constants import YES, NO
from edc_base.utils import formatted_age

tz = pytz.timezone(settings.TIME_ZONE)


class BaseConsentForm(ModelForm):
    """Form for models that are a subclass of BaseConsent."""

    def get_model_attr(self, attrname):
        """Returns the attribute's value from either the model or proxy model."""
        try:
            value = getattr(self._meta.model, attrname)
        except AttributeError:
            value = getattr(self._meta.model.proxy_for_model, attrname)
        return value

    def clean(self):
        cleaned_data = super(BaseConsentForm, self).clean()
        self.clean_identity_and_confirm_identity()
        self.clean_identity_with_unique_fields()
        self.clean_initials_with_full_name()
        self.clean_dob_relative_to_consent_datetime()
        self.clean_guardian_and_dob()
        self.clean_is_literate_and_witness()
        return cleaned_data

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
        AGE_IS_ADULT = self.get_model_attr('AGE_IS_ADULT')
        rdelta = relativedelta(consent_datetime.date(), dob)
        if rdelta.years < AGE_IS_ADULT:
            if not guardian:
                raise ValidationError(
                    'Subject\'s age is %(age)s. Subject is a minor. Guardian\'s '
                    'name is required with signature on the paper document.',
                    params={'age': formatted_age(dob, consent_datetime.date())},
                    code='invalid')
        if rdelta.years >= AGE_IS_ADULT and guardian:
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
        MIN_AGE_OF_CONSENT = self.get_model_attr('MIN_AGE_OF_CONSENT')
        MAX_AGE_OF_CONSENT = self.get_model_attr('MAX_AGE_OF_CONSENT')
        rdelta = relativedelta(consent_datetime.date(), dob)
        if rdelta.years < MIN_AGE_OF_CONSENT:
            raise ValidationError(
                'Subject\'s age is %(age)s. Subject is not eligible for consent.',
                params={'age': formatted_age(dob, consent_datetime.date())},
                code='invalid')
        if rdelta.years > MAX_AGE_OF_CONSENT:
            raise ValidationError(
                'Subject\'s age is %(age)s. Subject is not eligible for consent.',
                params={'age': formatted_age(dob, consent_datetime.date())},
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

    def clean_gender(self):
        """Validates gender is a gender of consent."""
        gender = self.cleaned_data.get("gender")
        GENDER_OF_CONSENT = self.get_model_attr('GENDER_OF_CONSENT')
        if gender not in GENDER_OF_CONSENT:
            raise ValidationError(
                'Gender of consent can only be \'%(gender_of_consent)s\'. Got \'%(gender)s\'.',
                params={'gender_of_consent': '\' or \''.join(GENDER_OF_CONSENT), 'gender': gender},
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
