from django import forms

from ..models import SubjectLocator
from ..modelform_mixins import LocatorModelFormMixin


class SubjectLocatorForm(LocatorModelFormMixin, forms.ModelForm):

    class Meta:
        model = SubjectLocator
        fields = '__all__'
