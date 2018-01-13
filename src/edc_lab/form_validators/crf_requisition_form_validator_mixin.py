from arrow.arrow import Arrow
from django import forms
from django.conf import settings
from django.utils import timezone
from edc_base.utils import convert_php_dateformat


class CrfRequisitionFormValidatorMixin:

    def validate_requisition(self, requisition_field, assay_datetime_field, *panels):
        requisition = self.cleaned_data.get(requisition_field)
        if requisition and requisition.panel_object not in panels:
            raise forms.ValidationError(
                {requisition_field: 'Incorrect requisition.'})

        self.required_if_true(
            requisition,
            field_required=assay_datetime_field)

        self.validate_assay_datetime(requisition, assay_datetime_field)

    def validate_assay_datetime(self, requisition, assay_datetime_field):
        assay_datetime = self.cleaned_data.get(assay_datetime_field)
        if assay_datetime:
            assay_datetime = Arrow.fromdatetime(
                assay_datetime, assay_datetime.tzinfo).to('utc').datetime
            if assay_datetime < requisition.requisition_datetime:
                formatted = timezone.localtime(requisition.requisition_datetime).strftime(
                    convert_php_dateformat(settings.SHORT_DATETIME_FORMAT))
                raise forms.ValidationError({
                    assay_datetime_field: (f'Invalid. Cannot be before date of '
                                           f'requisition {formatted}.')})
