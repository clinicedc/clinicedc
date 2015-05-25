from datetime import date
from dateutil.relativedelta import relativedelta
from django.utils import dateparse
from django import forms
from edc.core.bhp_variables.models import StudySpecific
from edc.core.bhp_variables.choices import GENDER_OF_CONSENT
from edc.core.bhp_common.utils import formatted_age
from edc.base.form.forms import BaseModelForm
from edc.core.crypto_fields.fields import BaseEncryptedField


class BaseSubjectConsentForm(BaseModelForm):
    """Form for models that are a subclass of BaseConsent."""
    def clean(self):

        if not cleaned_data.get("gender", None):
            raise forms.ValidationError('Please specify the gender')

        for field in self._meta.model._meta.fields:
            if isinstance(field, BaseEncryptedField):
                field.validate_with_cleaned_data(field.attname, cleaned_data)

        """
        if minor, force specify guardian's name
        """
        try:
            obj = StudySpecific.objects.all()[0]
        except IndexError:
            raise TypeError("Please add your bhp_variables site specifics")


        validate_age(self):            
        # check if guardian name is required
            # guardian name is required if subject is a minor but the field may not be on the form
            # if the study does not have minors.
        self.validate_guardian_name()
        # if edc_consent model has a ConsentAge method that returns an ordered range of ages as list
        if hasattr(self._meta.model, 'ConsentAge'):
            instance = self._meta.model()
            consent_age_range = instance.ConsentAge()
            rdelta = relativedelta(self.consent_datetime, cleaned_data.get('dob'))
            if rdelta.years not in consent_age_range:
                raise forms.ValidationError("Invalid Date of Birth. Age of edc_consent must be between %sy and %sy inclusive. Got %sy" % (consent_age_range[0], consent_age_range[-1], rdelta.years,))

        # check for gender of edc_consent
        if cleaned_data.get('gender'):
            study_specific = StudySpecific.objects.all()[0]
            gender_of_consent = study_specific.gender_of_consent
            if gender_of_consent == 'MF':
                allowed = ('MF', 'Male and Female')
                entry = ('value', cleaned_data.get('gender'))
            else:
                for lst in GENDER_OF_CONSENT:
                    if lst[0] == gender_of_consent:
                        allowed = lst
                for lst in GENDER_OF_CONSENT:
                    if lst[0] == cleaned_data.get('gender'):
                        entry = lst
            if cleaned_data.get('gender') != allowed[0] and allowed[0] != 'MF':
                raise forms.ValidationError(u'Gender of edc_consent is %s. You entered %s.' % (allowed[1], entry[1]))
        # confirm attr identity and confirm_identity match
        if cleaned_data.get('identity') and cleaned_data.get('confirm_identity'):
            if cleaned_data.get('identity') != cleaned_data.get('confirm_identity'):
                raise forms.ValidationError('Identity mismatch. Identity number must match the confirmation field.')
        # edc_consent cannot be submitted if answer is none to last four edc_consent questions
        if not cleaned_data.get('consent_reviewed', None) or cleaned_data.get('consent_reviewed', None) == 'No':
            raise forms.ValidationError('If edc_consent reviewed is No, patient cannot be enrolled')
        if not cleaned_data.get('study_questions', None) or cleaned_data.get('study_questions', None) == 'No':
            raise forms.ValidationError('If unable to answer questions from client and/or None, patient cannot be enrolled')
        if 'assessment_score' in cleaned_data:
            if not cleaned_data.get('assessment_score', None) or cleaned_data.get('assessment_score', None) == 'No':
                raise forms.ValidationError('Client assessment should at least be a passing score. If No, patient cannot be enrolled')
        if not self.accepted_consent_copy(cleaned_data):
            raise forms.ValidationError('If patient has not been given edc_consent copy and/or None, patient cannot be enrolled')

        if cleaned_data.get('is_literate', None) == 'No' and not cleaned_data.get('witness_name', None):
            raise forms.ValidationError('You wrote subject is illiterate. Please provide the name of a witness here and with signature on the paper document.')
        if cleaned_data.get('is_literate') == 'Yes' and cleaned_data.get('witness_name', None):
            raise forms.ValidationError('You wrote subject is literate. The name of a witness is NOT required.')
        # Always return the full collection of cleaned data.
        return super(BaseSubjectConsentForm, self).clean()

    def accepted_consent_copy(self, cleaned_data):
        if not cleaned_data.get('consent_copy', None) or cleaned_data.get('consent_copy', None) == 'No':
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
    def dob(self, dob):
        return self.cleaned_data.get('dob')

    def validate_age(self):
        if self.dob:
            rdelta = relativedelta(self.consent_datetime, self.dob)
            if rdelta.years < obj.minimum_age_of_consent:
                raise forms.ValidationError(
                    'Subject\'s age is {}. Subject is not eligible for informated consent.'.format(
                        formatted_age(self.dob, date.today())))

    def validate_guardian(self):
        rdelta = relativedelta(self.consent_datetime, self.dob)
        if rdelta.years < obj.age_at_adult_lower_bound:
            if "guardian_name" not in cleaned_data.keys():
                raise forms.ValidationError('Subject is a minor. "guardian_name" is required but missing from the form. Please add this field to the form.')
            elif not cleaned_data.get("guardian_name", None):
                raise forms.ValidationError(u'Subject\'s age is %s. Subject is a minor. Guardian\'s name is required here and with signature on the paper document.' % (formatted_age(cleaned_data.get('dob'), date.today())))
            # elif not re.match(r'\w+\,\ \w+', cleaned_data.get("guardian_name", '')):
            #    raise forms.ValidationError('Invalid format for guardian name. Expected format \'FIRSTNAME, LASTNAME\'.')
            else:
                pass
        if rdelta.years >= obj.age_at_adult_lower_bound and "guardian_name" in cleaned_data.keys():
            if not cleaned_data.get("guardian_name", None) == '':
                raise forms.ValidationError(u'Subject\'s age is %s. Subject is an adult. Guardian\'s name is NOT required.' % (formatted_age(cleaned_data.get('dob'), date.today())))
