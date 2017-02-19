from django import forms

from django.core.exceptions import FieldError

from edc_constants.constants import YES, NO


class RequisitionFormMixin(forms.ModelForm):

    def clean(self):
        cleaned_data = super(RequisitionFormMixin, self).clean()
        if cleaned_data.get('is_drawn').lower() == YES and not cleaned_data.get('drawn_datetime'):
            raise forms.ValidationError("A specimen was collected. Please provide the date and time collected.")
        if cleaned_data.get('is_drawn').lower() == NO and not cleaned_data.get('reason_not_drawn'):
            raise forms.ValidationError("Please provide a reason why the specimen was not collected.")
        if cleaned_data.get('is_drawn').lower() == YES and cleaned_data.get('reason_not_drawn'):
            raise forms.ValidationError(
                "A specimen was not drawn. Do not provided a reason why it was not collected.")
        return cleaned_data


class PackingListFormMixin(forms.ModelForm):

    """
    The "requisition" model is required for the code
    in the clean() method below.

    In the local xxxx_lab app add something this to forms

    from lab_packing.forms import PackingListForm

    class PackingListForm (BasePackingListForm):

        def clean(self):
            self.requisition  = [InfantRequisition,]
            return  super(PackingListForm, self).clean()

        class Meta:
            model = PackingList"""
    requisition = None

    def clean(self):
        cleaned_data = super(PackingListFormMixin, self).clean()
        if not self.requisition:
            raise forms.ValidationError(
                'Class attribute requisition cannot be None. '
                'Was it not defined in the local \'..._lab\' forms.py app?')
        if not isinstance(self.requisition, list):
            self.requisition = [self.requisition, ]
        if not cleaned_data.get('list_items'):
            raise forms.ValidationError(
                'Please indicate at least one specimen identifier to add to the packing list')
        else:
            for specimen_identifier in cleaned_data.get('list_items').replace('\r', '').split('\n'):
                if specimen_identifier:
                    found = False
                    for requisition in self.requisition:
                        try:
                            if requisition.objects.filter(specimen_identifier=specimen_identifier):
                                found = True
                                break
                            elif requisition.objects.filter(requisition_identifier=specimen_identifier[4:-4]):
                                found = True
                                break
                        except FieldError:
                            if requisition.objects.filter(aliquot_identifier=specimen_identifier):
                                found = True
                                break
                    if not found:
                        raise forms.ValidationError(
                            '{} specimen identifier \'{}\' not found'.format(
                                requisition._meta.verbose_name, specimen_identifier,))
        return cleaned_data


class PackingListItemFormMixin(forms.ModelForm):

    def clean(self):
        cleaned_data = super(PackingListItemFormMixin, self).clean()
        return cleaned_data
