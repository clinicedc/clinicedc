from django import forms

from .models import SubjectScreening


class SubjectScreeningForm(forms.ModelForm):
    class Meta:
        model = SubjectScreening
        fields = "__all__"
