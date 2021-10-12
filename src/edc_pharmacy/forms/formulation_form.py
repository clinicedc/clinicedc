from django import forms

from ..models import Formulation


class FormulationForm(forms.ModelForm):
    class Meta:
        model = Formulation
        fields = "__all__"
