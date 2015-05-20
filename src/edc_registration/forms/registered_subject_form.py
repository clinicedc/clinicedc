from edc.base.form.forms import BaseModelForm
from ..models import RegisteredSubject


class RegisteredSubjectForm (BaseModelForm):
    """Form for the RegisteredSubject model."""

    class Meta:
        model = RegisteredSubject
