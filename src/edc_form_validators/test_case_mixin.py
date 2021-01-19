from django.forms import ValidationError


class FormValidatorTestCaseMixin:

    form_validator_default_form_cls = None

    def validate_form_validator(self, cleaned_data, form_cls=None):
        form_cls = form_cls or self.form_validator_default_form_cls
        form_validator = form_cls(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError:
            pass
        return form_validator
