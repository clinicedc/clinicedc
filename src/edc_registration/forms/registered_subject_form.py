from django import forms

from ..models import RegisteredSubject


class RegisteredSubjectForm (forms.ModelForm):
    """Form for the RegisteredSubject model."""

    class Meta:
        model = RegisteredSubject
