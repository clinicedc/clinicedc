from django import forms


class FormValidatorMixin:
    """A ModelForm mixin to add a validator class.

    Declare with `forms.ModelForm`.
    """

    form_validator_cls = None

    def clean(self):
        cleaned_data = super().clean()
        try:
            form_validator = self.form_validator_cls(
                cleaned_data=cleaned_data, instance=self.instance
            )
        except TypeError:
            pass
        else:
            cleaned_data = form_validator.validate()
        return cleaned_data
