from datetime import date
from dateutil.relativedelta import relativedelta

from django import forms
from django.conf import settings

from edc_base.utils import formatted_age
from edc_constants.constants import YES, NO


class BaseSubjectConsentForm(forms.ModelForm):
    """Form for models that are a subclass of BaseConsent."""
    def clean(self):
        cleaned_data = self.cleaned_data
        if not cleaned_data.get("gender", None):
            raise forms.ValidationError('Please specify the gender')

#         for field in self._meta.model._meta.fields:
#             if isinstance(field, BaseEncryptedField):
#                 field.validate_with_cleaned_data(field.attname, cleaned_data)

        self.validate_age()
        self.validate_guardian(cleaned_data)
        # if edc_consent model has a ConsentAge method that returns an ordered range of ages as list
        if hasattr(self._meta.model, 'ConsentAge'):
            instance = self._meta.model()
            consent_age_range = instance.ConsentAge()
            rdelta = relativedelta(self.consent_datetime, cleaned_data.get('dob'))
            if rdelta.years not in consent_age_range:
                raise forms.ValidationError(
                    'Invalid Date of Birth. Age of edc_consent must be '
                    'between {}y and {}y inclusive. Got {}y'.format(
                        consent_age_range[0], consent_age_range[-1], rdelta.years,))

        self.validate_gender(cleaned_data)
        self.validate_identity(cleaned_data)
        # edc_consent cannot be submitted if answer is none to last four edc_consent questions
        self.validate_audit_questions(cleaned_data)
        # Always return the full collection of cleaned data.
        return super(BaseSubjectConsentForm, self).clean()

    def accepted_consent_copy(self, cleaned_data):
        if not cleaned_data.get('consent_copy', None) or cleaned_data.get('consent_copy', None) == NO:
            return False
        else:
            return True

    @property
    def consent_datetime(self):
        """Returns date the subject was consented.

        We validate consent age against the time of consent and not now()."""
        try:
            return self.cleaned_data.get('consent_datetime').date()
        except AttributeError:
            return date.today()

    @property
    def dob(self):
        return self.cleaned_data.get('dob')

    def validate_age(self):
        """Validates age in consent range."""
        if self.dob:
            rdelta = relativedelta(self.consent_datetime, self.dob)
            if rdelta.years < settings.MINIMUM_AGE_OF_CONSENT:
                raise forms.ValidationError(
                    'Subject\'s age is {}. Subject is not eligible for informated consent.'.format(
                        formatted_age(self.dob, date.today())))

    def validate_guardian(self, cleaned_data):
        """ Forces guardian's name if minor."""
        rdelta = relativedelta(self.consent_datetime, self.dob)
        if rdelta.years < settings.AGE_IS_ADULT:
            if "guardian_name" not in cleaned_data:
                raise forms.ValidationError(
                    'Subject is a minor. "guardian_name" is required but missing from the form. '
                    'Please add this field to the form.')
            elif not cleaned_data.get("guardian_name", None):
                raise forms.ValidationError(
                    'Subject\'s age is {}. Subject is a minor. Guardian\'s name is required '
                    'here and with signature on the paper document.'.format(
                        formatted_age(cleaned_data.get('dob'), date.today())))
            else:
                pass
        if rdelta.years >= settings.AGE_IS_ADULT and "guardian_name" in cleaned_data.keys():
            if not cleaned_data.get("guardian_name", None) == '':
                raise forms.ValidationError(
                    'Subject\'s age is {}. Subject is an adult. Guardian\'s name is NOT '
                    'required.'.format(formatted_age(cleaned_data.get('dob'), date.today())))

    def validate_gender(self, cleaned_data):
        """Validates gender of edc_consent."""
        if cleaned_data.get('gender'):
            if cleaned_data.get('gender') not in settings.GENDER_OF_CONSENT:
                raise forms.ValidationError(
                    'Gender of edc_consent must be in {}. You entered {}.'.format(
                        settings.GENDER_OF_CONSENT, cleaned_data.get('gender')))

    def validate_identity(self, cleaned_data):
        """Validate identity and confirm_identity match."""
        if cleaned_data.get('identity') and cleaned_data.get('confirm_identity'):
            if cleaned_data.get('identity') != cleaned_data.get('confirm_identity'):
                raise forms.ValidationError(
                    'Identity mismatch. Identity number must match the confirmation field.')

    def validate_audit_questions(self, cleaned_data):
        if not cleaned_data.get('consent_reviewed', None) or cleaned_data.get('consent_reviewed', None) == NO:
            raise forms.ValidationError('If edc_consent reviewed is No, patient cannot be enrolled')
        if not cleaned_data.get('study_questions', None) or cleaned_data.get('study_questions', None) == NO:
            raise forms.ValidationError(
                'If unable to answer questions from client and/or None, patient cannot be enrolled')
        if 'assessment_score' in cleaned_data:
            if not cleaned_data.get('assessment_score', None) or cleaned_data.get('assessment_score', None) == NO:
                raise forms.ValidationError(
                    'Client assessment should at least be a passing score. If No, patient cannot be enrolled')
        if not self.accepted_consent_copy(cleaned_data):
            raise forms.ValidationError(
                'If patient has not been given edc_consent copy and/or None, patient cannot be enrolled')
        if cleaned_data.get('is_literate', None) == NO and not cleaned_data.get('witness_name', None):
            raise forms.ValidationError(
                'You wrote subject is illiterate. Please provide the name of a witness '
                'here and with signature on the paper document.')
        if cleaned_data.get('is_literate') == YES and cleaned_data.get('witness_name', None):
            raise forms.ValidationError(
                'You wrote subject is literate. The name of a witness is NOT required.')
