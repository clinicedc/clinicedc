import re

from django import forms

from edc_base.modelform_validators import OtherSpecifyFieldValidator

from ..models import Box


class BoxForm(OtherSpecifyFieldValidator, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('specimen_types'):
            pattern = '([1-9][0-9]*[ ]*,[ ]*)*[1-9][0-9]*'
            match = re.match(pattern, cleaned_data.get('specimen_types'))
            if not match:
                raise forms.ValidationError(
                    {'specimen_types': 'Invalid list of specimen types.'},
                    code='invalid format')
            elif match.group() != cleaned_data.get('specimen_types'):
                raise forms.ValidationError(
                    {'specimen_types': 'Invalid list of specimen types.'},
                    code='invalid format')
            else:
                specimen_types = [code.strip()
                                  for code in match.group().split(',')]
                if len(specimen_types) != len(list(set(specimen_types))):
                    raise forms.ValidationError(
                        {'specimen_types': 'List must be unique.'},
                        code='list not unique')
            cleaned_data['specimen_types'] = ','.join(specimen_types)
        self.validate_other_specify('category')
        return cleaned_data

    class Meta:
        fields = '__all__'
        model = Box
