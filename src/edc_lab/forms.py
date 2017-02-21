import re

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from edc_base.modelform_mixins import OtherSpecifyValidationMixin

from .models import Destination, Manifest


class AliquotForm(forms.ModelForm):

    aliquot_identifier = forms.CharField(
        label='Aliquot identifier',
        disabled=True)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class PackAliquotsForm(forms.Form):

    aliquot_identifiers = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manifest'] = forms.ChoiceField(
            choices=self.manifest_choices)
        self.fields['destination'] = forms.ChoiceField(
            choices=[(obj.name, str(obj)) for obj in Destination.objects.all()])
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = 'edc-lab:pack_aliquots_url'
        self.helper.html5_required = True
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

    @property
    def manifest_choices(self):
        choices = [('new', 'New manifest')]
        for obj in Manifest.objects.filter(shipped=False).order_by(
                '-manifest_identifier'):
            choices.append((obj.manifest_identifier, str(obj)))
        return choices


class BoxForm(OtherSpecifyValidationMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('specimen_types'):
            pattern = '([1-9][0-9]*[ ]*,[ ]*)*[1-9][0-9]*'
            match = re.match(pattern, cleaned_data.get('specimen_types'))
            if not match:
                raise forms.ValidationError({
                    'specimen_types':
                    'Invalid list of specimen types.'})
            elif match.group() != cleaned_data.get('specimen_types'):
                raise forms.ValidationError({
                    'specimen_types':
                    'Invalid list of specimen types.'})
            else:
                specimen_types = [code.strip()
                                  for code in match.group().split(',')]
                if len(specimen_types) != len(list(set(specimen_types))):
                    raise forms.ValidationError({
                        'specimen_types':
                        'List must be unique.'})

        self.validate_other_specify('category')
        return cleaned_data


class BoxTypeForm(OtherSpecifyValidationMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('across') * cleaned_data.get('down') != cleaned_data.get('total'):
            raise forms.ValidationError('Invalid dimensions or total')
        return cleaned_data


class BoxItemForm(OtherSpecifyValidationMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class SimpleBoxItemForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    class Meta:
        fields = ('identifier',)
