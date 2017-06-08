from django import forms
from django.apps import apps as django_apps

from edc_base.modelform_validators import (
    ApplicableFieldValidator, RequiredFieldValidator)
from edc_constants.constants import YES, NO


class RequisitionFormMixin(ApplicableFieldValidator, RequiredFieldValidator):

    aliquot_model = django_apps.get_model(
        *django_apps.get_app_config('edc_lab').aliquot_model.split('.'))
    default_item_type = 'tube'
    default_item_count = 1
    default_estimated_volume = 5.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not kwargs.get('instance'):
            self.fields['item_type'].initial = self.default_item_type
            self.fields['item_count'].initial = self.default_item_count
            self.fields[
                'estimated_volume'].initial = self.default_estimated_volume
        self.fields['panel_name'].widget.attrs['readonly'] = True
        if self.fields.get('specimen_type'):
            self.fields['specimen_type'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('packed') != self.instance.packed:
            raise forms.ValidationError({
                'packed':
                'Value may not be changed here.'})
        elif cleaned_data.get('processed') != self.instance.processed:
            if self.aliquot_model.objects.filter(
                    requisition_identifier=self.instance.requisition_identifier).exists():
                raise forms.ValidationError(
                    {'processed': 'Value may not be changed. Aliquots exist.'})
        elif not cleaned_data.get('received') and self.instance.received:
            if self.instance.processed:
                raise forms.ValidationError(
                    {'received': 'Specimen has already been processed.'})
        elif cleaned_data.get('received') and not self.instance.received:
            raise forms.ValidationError({
                'received':
                'Receive specimens in the lab section of the EDC.'})
        elif self.instance.received:
            raise forms.ValidationError(
                'Requisition may not be changed. The specimen has '
                'already been received.')

        self.applicable_if(
            NO, field='is_drawn', field_applicable='reason_not_drawn')
        self.required_if(
            YES, field='is_drawn', field_required='drawn_datetime')
        self.applicable_if(
            YES, field='is_drawn', field_applicable='item_type')
        self.required_if(
            YES, field='is_drawn', field_required='item_count')
        self.required_if(
            YES, field='is_drawn', field_required='estimated_volume')

        return cleaned_data
