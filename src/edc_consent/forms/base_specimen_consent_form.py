from django import forms

from edc_constants.constants import YES, NO


class BaseSpecimenConsentForm(forms.ModelForm):

    # TODO: This code needs to be updated!!

    STUDY_CONSENT = None

    def clean(self):
        cleaned_data = super(BaseSpecimenConsentForm, self).clean()
        study_consent = self.study_consent_or_raise()
        self.compare_attr_to_study_consent('is_literate', study_consent)
        self.compare_attr_to_study_consent('witness_name', study_consent)
        self.purpose_explained_and_understood(study_consent)
        self.copy_of_consent_provided()
        return cleaned_data

    def study_consent_or_raise(self):
        """Returns an instance of the current maternal consent or
        raises an exception if not found."""
        cleaned_data = self.cleaned_data
        subject_identifier = cleaned_data.get('subject_identifier')
        consent_datetime = cleaned_data.get('consent_datetime')
        maternal_consent = self.STUDY_CONSENT.consent.valid_consent_for_period(
            subject_identifier, consent_datetime)
        if not maternal_consent:
            raise forms.ValidationError(
                'Maternal consent must be completed before the specimen consent.')
        return maternal_consent

    def compare_attr_to_study_consent(self, attrname, study_consent):
        """Compares the value of a specimen consent attribute to that on the
        study consent and raises if the values are not equal."""
        cleaned_data = self.cleaned_data
        value = cleaned_data.get(attrname)
        study_consent_value = getattr(study_consent, attrname)
        if value != study_consent_value:
            fields = [field for field in study_consent._meta.fields if field.name == attrname]
            raise forms.ValidationError(
                'Specimen consent and maternal consent do not match for question '
                '\'{}\'. Got {} != {}. Please correct.'.format(
                    ', '.join([fld.verbose_name for fld in fields]),
                    value, study_consent_value))

    def purpose_explained_and_understood(self, study_consent):
        """Ensures the purpose of specimen storage is indicated as
        explained and understood."""
        cleaned_data = self.cleaned_data
        if cleaned_data.get("may_store_samples") == YES:
            if cleaned_data.get("purpose_explained") != YES:
                raise forms.ValidationError(
                    "If the participant agrees for specimens to be stored, "
                    "ensure that purpose of specimen storage is explained.")
            if cleaned_data.get("purpose_understood") != YES:
                raise forms.ValidationError(
                    "If the participant agrees for specimens to be stored, "
                    "ensure that participant understands the purpose, procedures "
                    "and benefits of specimen storage.")

    def copy_of_consent_provided(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get("may_store_samples") == NO:
            if cleaned_data.get('offered_copy') != NO:
                raise forms.ValidationError(
                    'Participant did not agree for specimens to be stored. '
                    'Do not provide the participant with a copy of the specimen consent.')
