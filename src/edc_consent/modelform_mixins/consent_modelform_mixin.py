from dateutil.relativedelta import relativedelta

from django import forms
from django.forms.utils import ErrorList
from django.utils import timezone

from edc_base.modelform_mixins import CommonCleanModelFormMixin
from edc_base.utils import formatted_age
from edc_constants.constants import YES, NO

from ..exceptions import SiteConsentError
from ..site_consents import site_consents


class ConsentModelFormMixin(CommonCleanModelFormMixin):
    """Form for models that are a subclass of BaseConsent."""

    confirm_identity = forms.CharField(
        label='Confirm identity',
        help_text="Retype the identity number")

    def clean(self):
        cleaned_data = super().clean()
        self.clean_initials_with_full_name()
        self.clean_gender_of_consent()
        self.clean_is_literate_and_witness()
        self.clean_dob_relative_to_consent_datetime()
        self.clean_guardian_and_dob()
        self.clean_identity_and_confirm_identity()
        self.clean_identity_with_unique_fields()
        return cleaned_data

    @property
    def consent_config(self):
        cleaned_data = self.cleaned_data
        try:
            consent_config = site_consents.get_consent(
                report_datetime=cleaned_data.get(
                    'consent_datetime') or self.instance.consent_datetime,
                consent_model=self._meta.model._meta.label_lower,
                consent_group=self._meta.model._meta.consent_group
            )
        except SiteConsentError as e:
            raise forms.ValidationError(e)
        return consent_config

    def clean_identity_and_confirm_identity(self):
        cleaned_data = self.cleaned_data
        identity = cleaned_data.get('identity')
        confirm_identity = cleaned_data.get('confirm_identity')
        if identity != confirm_identity:
            raise forms.ValidationError(
                {'identity': 'Identity mismatch. Identity must match '
                 'the confirmation field. Got {} != {}'.format(
                     identity, confirm_identity)},
                params={
                    'identity': identity, 'confirm_identity': confirm_identity},
                code='invalid')

    def clean_identity_with_unique_fields(self):
        cleaned_data = self.cleaned_data
        identity = cleaned_data.get('identity')
        first_name = cleaned_data.get('first_name')
        initials = cleaned_data.get('initials')
        dob = cleaned_data.get('dob')
        unique_together_form = self.unique_together_string(
            first_name, initials, dob)
        for consent in self._meta.model.objects.filter(identity=identity):
            unique_together_model = self.unique_together_string(
                consent.first_name, consent.initials, consent.dob)
            if unique_together_form != unique_together_model:
                raise forms.ValidationError(
                    {'identity': 'Identity \'{}\' is already in use by subject {}. '
                     'Please resolve.'.format(identity, consent.subject_identifier)},
                    params={
                        'subject_identifier': consent.subject_identifier,
                        'identity': identity},
                    code='invalid')
        for consent in self._meta.model.objects.filter(
                first_name=first_name, initials=initials, dob=dob):
            if consent.identity != identity:
                raise forms.ValidationError(
                    'Subject\'s identity was previously reported as \'{}\'. '
                    'You wrote \'{}\'. Please resolve.'.format(
                        consent.identity, identity),
                    params={
                        'existing_identity': consent.identity, 'identity': identity},
                    code='invalid')

    # ok
    def clean_initials_with_full_name(self):
        cleaned_data = self.cleaned_data
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        initials = cleaned_data.get("initials")
        try:
            if initials[:1] != first_name[:1] or initials[-1:] != last_name[:1]:
                raise forms.ValidationError(
                    {'initials': 'Initials do not match full name.'},
                    params={
                        'initials': initials,
                        'first_name': first_name,
                        'last_name': last_name},
                    code='invalid')
        except (IndexError, TypeError):
            raise forms.ValidationError('Initials do not match fullname.')

    def clean_guardian_and_dob(self):
        """Validates if guardian is required based in AGE_IS_ADULT
        set on the model.
        """
        cleaned_data = self.cleaned_data
        guardian = cleaned_data.get("guardian_name")
        dob = cleaned_data.get('dob')
        consent_datetime = timezone.localtime(
            cleaned_data.get('consent_datetime', self.instance.consent_datetime))
        rdelta = relativedelta(consent_datetime.date(), dob)
        if rdelta.years < self.consent_config.age_is_adult:
            if not guardian:
                raise forms.ValidationError(
                    'Subject\'s age is {}. Subject is a minor. Guardian\'s '
                    'name is required with signature on the paper '
                    'document.'.format(
                        formatted_age(dob, consent_datetime)),
                    params={'age': formatted_age(dob, consent_datetime)},
                    code='invalid')
        if rdelta.years >= self.consent_config.age_is_adult and guardian:
            if guardian:
                raise forms.ValidationError(
                    'Subject\'s age is {}. Subject is an adult. Guardian\'s '
                    'name is NOT required.'.format(
                        formatted_age(dob, consent_datetime)),
                    params={'age': formatted_age(dob, consent_datetime)},
                    code='invalid')

    def clean_dob_relative_to_consent_datetime(self):
        """Validates that the dob is within the bounds of MIN and
        MAX set on the model.
        """
        cleaned_data = self.cleaned_data
        dob = cleaned_data.get('dob')
        consent_datetime = cleaned_data.get(
            'consent_datetime', self.instance.consent_datetime)
        if not consent_datetime:
            self._errors["consent_datetime"] = ErrorList(
                [u"This field is required. Please fill consent date and time."])
            raise forms.ValidationError('Please correct the errors below.')
        rdelta = relativedelta(consent_datetime.date(), dob)
        if rdelta.years > self.consent_config.age_max:
            raise forms.ValidationError(
                'Subject\'s age is %(age)s. Subject is not eligible for '
                'consent. Maximum age of consent is %(max)s.',
                params={
                    'age': formatted_age(dob, consent_datetime),
                    'max': self.consent_config.age_max},
                code='invalid')
        if rdelta.years < self.consent_config.age_min:
            raise forms.ValidationError(
                'Subject\'s age is %(age)s. Subject is not eligible for '
                'consent. Minimum age of consent is %(min)s.',
                params={
                    'age': formatted_age(dob, consent_datetime),
                    'min': self.consent_config.age_min},
                code='invalid')

    def clean_is_literate_and_witness(self):
        cleaned_data = self.cleaned_data
        is_literate = cleaned_data.get('is_literate')
        witness_name = cleaned_data.get('witness_name')
        if is_literate == NO and not witness_name:
            raise forms.ValidationError(
                'You wrote subject is illiterate. Please provide the '
                'name of a witness on this form and signature on the '
                'paper document.',
                code='invalid')
        if is_literate == YES and witness_name:
            raise forms.ValidationError(
                'You wrote subject is literate. The name of a witness '
                'is NOT required.',
                code='invalid')
        return is_literate

    def clean_consent_reviewed(self):
        consent_reviewed = self.cleaned_data.get('consent_reviewed')
        if consent_reviewed != YES:
            raise forms.ValidationError(
                'Consent has not been reviewed with the Subject.',
                code='invalid')
        return consent_reviewed

    def clean_study_questions(self):
        study_questions = self.cleaned_data.get('study_questions')
        if study_questions != YES:
            raise forms.ValidationError(
                'Subject\'s questions related to the consent have not '
                'been answer or discussed.',
                code='invalid')
        return study_questions

    def clean_assessment_score(self):
        assessment_score = self.cleaned_data.get('assessment_score')
        if assessment_score != YES:
            raise forms.ValidationError(
                'The scored assessment of the subject\'s understanding '
                'of the consent should at least be passing.',
                code='invalid')
        return assessment_score

    def clean_consent_copy(self):
        consent_copy = self.cleaned_data.get('consent_copy')
        if consent_copy == NO:
            raise forms.ValidationError(
                'The subject has not been given a copy of the consent.',
                code='invalid')
        return consent_copy

    def clean_consent_signature(self):
        consent_signature = self.cleaned_data.get('consent_signature')
        if consent_signature != YES:
            raise forms.ValidationError(
                'The subject has not signed the consent.',
                code='invalid')
        return consent_signature

    def clean_gender_of_consent(self):
        """Validates gender is a gender of consent."""
        gender = self.cleaned_data.get("gender")
        if gender not in self.consent_config.gender:
            raise forms.ValidationError(
                'Gender of consent can only be \'%(gender_of_consent)s\'. '
                'Got \'%(gender)s\'.',
                params={'gender_of_consent': '\' or \''.join(
                    self.consent_config.gender), 'gender': gender},
                code='invalid')
        return gender

    def unique_together_string(self, first_name, initials, dob):
        try:
            dob = dob.isoformat()
        except AttributeError:
            dob = ''
        return '{}{}{}'.format(first_name, dob, initials)
