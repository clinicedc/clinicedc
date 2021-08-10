from django.forms import ModelForm


class FormValidatorMixin:
    """A ModelForm mixin to add a validator class.

    Declare with `forms.ModelForm`.
    """

    form_validator_cls = None

    def clean(self: ModelForm) -> dict:
        cleaned_data = super().clean()  # type: ignore
        try:
            form_validator = self.form_validator_cls(
                cleaned_data=cleaned_data, instance=self.instance, data=self.data
            )
        except TypeError as e:
            if str(e) != "'NoneType' object is not callable":
                raise
        else:
            cleaned_data = form_validator.validate()
        return cleaned_data
