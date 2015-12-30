from django import forms
from ..models import SubjectConfiguration


class SubjectConfigurationForm (forms.ModelForm):
    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data

    class Meta:
        model = SubjectConfiguration
