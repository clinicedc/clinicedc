from arrow.arrow import Arrow
from django import forms
from django.conf import settings
from django.utils import timezone
from edc_base.utils import convert_php_dateformat
from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator

from ..models import Aliquot


class RequisitionFormMixin:

    aliquot_model = Aliquot
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

        self.validate_requisition_datetime()

        form_validator = FormValidator(
            cleaned_data=cleaned_data,
            instance=self.instance)
        form_validator.applicable_if(
            NO, field='is_drawn', field_applicable='reason_not_drawn')
        form_validator.validate_other_specify(field='reason_not_drawn')
        form_validator.required_if(
            YES, field='is_drawn', field_required='drawn_datetime')
        form_validator.applicable_if(
            YES, field='is_drawn', field_applicable='item_type')
        form_validator.required_if(
            YES, field='is_drawn', field_required='item_count')
        form_validator.required_if(
            YES, field='is_drawn', field_required='estimated_volume')

        return cleaned_data

    def validate_assay_datetime(self, assay_datetime, requisition, field):
        if assay_datetime:
            assay_datetime = Arrow.fromdatetime(
                assay_datetime, assay_datetime.tzinfo).to('utc').datetime
            if assay_datetime < requisition.requisition_datetime:
                formatted = timezone.localtime(requisition.requisition_datetime).strftime(
                    convert_php_dateformat(settings.SHORT_DATETIME_FORMAT))
                raise forms.ValidationError({
                    field: (f'Invalid. Cannot be before date of '
                            f'requisition {formatted}.')})

    def validate_requisition_datetime(self):
        requisition_datetime = self.cleaned_data.get('requisition_datetime')
        subject_visit = self.cleaned_data.get('subject_visit')
        if requisition_datetime:
            requisition_datetime = Arrow.fromdatetime(
                requisition_datetime, requisition_datetime.tzinfo).to('utc').datetime
            if requisition_datetime < subject_visit.report_datetime:
                formatted = timezone.localtime(subject_visit.report_datetime).strftime(
                    convert_php_dateformat(settings.SHORT_DATETIME_FORMAT))
                raise forms.ValidationError({
                    'requisition_datetime':
                    f'Invalid. Cannot be before date of visit {formatted}.'})
