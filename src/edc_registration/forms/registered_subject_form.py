from django.forms import ModelForm

from ..models import RegisteredSubject


class RegisteredSubjectForm (ModelForm):
    """Form for the RegisteredSubject model."""

    class Meta:
        model = RegisteredSubject
        fields = "__all__"
