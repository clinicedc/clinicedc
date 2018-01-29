from django import forms
from edc_constants.constants import YES, NO
from edc_form_validators.form_validator import FormValidator


class SubjectLocatorFormValidator(FormValidator):

    def clean(self):
        self.validate_may_call_fields()

        self.required_if(
            YES, field='may_call_work', field_required='subject_work_place')
        self.not_required_if(
            NO, field='may_call_work',
            field_required='subject_work_phone', inverse=False)
        self.not_required_if(
            NO, field='may_call_work',
            field_required='subject_work_cell', inverse=False)

        self.required_if(
            YES, field='home_visit_permission', field_required='physical_address')
        self.required_if(
            YES, field='may_contact_someone', field_required='contact_name')
        self.required_if(
            YES, field='contact_name', field_required='contact_rel')
        self.required_if(
            YES, field='contact_name', field_required='contact_physical_address')

        self.required_if(
            YES, field='may_contact_indirectly',
            field_required='indirect_contact_name')
        self.required_if(
            YES, field='may_contact_indirectly',
            field_required='indirect_contact_relation')
        self.required_if(
            YES, field='may_contact_indirectly',
            field_required='indirect_contact_physical_address')

        for field in ['indirect_contact_cell', 'indirect_contact_cell_alt',
                      'indirect_contact_phone']:
            self.not_required_if(
                NO, field='may_contact_indirectly', field_required=field,
                inverse=False)

    def validate_may_call_fields(self):
        validations = {}
        number_fields = ['subject_cell', 'subject_phone']
        if self.cleaned_data.get('may_call') == YES:
            if all([self.cleaned_data.get(f) is None for f in number_fields]):
                validations = {
                    k: 'This field is required' for k in number_fields}
        elif self.cleaned_data.get('may_call') == NO:
            number_fields.extend(['subject_cell_alt', 'subject_phone_alt']),
            for field in number_fields:
                if self.cleaned_data.get(field):
                    validations.update({field: 'This field is not required.'})
        if validations:
            raise forms.ValidationError(validations)
