from django import forms

from ..models import SubjectLocator
from ..modelform_mixins import LocatorModelFormMixin


class SubjectLocatorForm(LocatorModelFormMixin, forms.ModelForm):

    subject_identifier = forms.CharField(
        label='Subject Identifier',
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = SubjectLocator
        fields = '__all__'
