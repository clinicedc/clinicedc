from arrow.arrow import Arrow
from django import forms
from django.conf import settings
from django.utils import timezone
from edc_base import convert_php_dateformat


class CrfRequisitionFormValidatorMixin:

    """An edc_form_validators.FormValidator mixin.

    Used with a CRF that refers to a requisition or requisitions.

    Call in FormValidator.clean.

    For test 'xxx' expects the field trio of 'xxx_requisition' and
    'xxx_assay_datetime', 'xxx_panel'

        self.required_if_true(
            self.cleaned_data.get('cd4') is not None,
            field_required='cd4_requisition')
        self.validate_requisition(
            'cd4_requisition', 'cd4_assay_datetime', cd4_panel)

    See also: ambition_validators.form_validators.blood_result
    """

    def validate_requisition(self, requisition_field, assay_datetime_field, *panels):
        """Validates that the requisition model instance exists
        and assay datetime provided.
        """
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
