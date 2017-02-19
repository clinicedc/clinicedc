from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Destination, Manifest


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
