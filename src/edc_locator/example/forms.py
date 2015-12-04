from django import forms

from edc_locator.forms import LocatorFormMixin
from .models import Locator


class LocatorForm(LocatorFormMixin, forms.ModelForm):

    class Meta:
        model = Locator
        fields = '__all__'
