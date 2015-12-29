from django import forms
from django.core.exceptions import FieldError

from edc_lab.lab_requisition.forms import BaseRequisitionForm

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
        model = PackingList

"""


class BasePackingListForm(BaseRequisitionForm):

    requisition = None

    def clean(self):

        cleaned_data = self.cleaned_data

        if not self.requisition:
            raise forms.ValidationError('Class attribute requisition cannot be None. Was it not defined in the local \'..._lab\' forms.py app?')
        if not isinstance(self.requisition, list):
            self.requisition = [self.requisition, ]
        if not cleaned_data.get('list_items'):
            raise forms.ValidationError('Please indicate at least one specimen identifier to add to the packing list')
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
                        raise forms.ValidationError('%s specimen identifier \'%s\' not found' % (requisition._meta.verbose_name, specimen_identifier,))
        return cleaned_data


class BasePackingListItemForm (forms.ModelForm):

    def clean(self):
        return super(BasePackingListItemForm, self).clean()
