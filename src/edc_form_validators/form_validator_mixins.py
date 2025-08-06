from __future__ import annotations

from django.forms import ModelForm

from edc_model_form.mixins.report_datetime_modelform_mixin import (
    ReportDatetimeModelFormMixin,
)


class FormValidatorMixin:
    """A ModelForm mixin to add a validator class.

    Declare with `forms.ModelForm`. If with multiple mixins,
    declare last before ModelForm:

        class MyForm(mixin1, mixin2, FormValidatorMixin, ModelForm):
            ...

    """

    form_validator_cls = None

    def clean(self: ModelForm) -> dict:
        cleaned_data = super().clean()
        try:
            form_validator = self.form_validator_cls(
                cleaned_data=cleaned_data,
                instance=self.instance,
                data=self.data,
                model=self._meta.model,
                current_site=getattr(self, "current_site", None),
                locale=getattr(self, "current_locale", None),
            )
        except TypeError as e:
            if str(e) != "'NoneType' object is not callable":
                raise
        else:
            cleaned_data = form_validator.validate()
        return cleaned_data


class ReportDatetimeFormValidatorMixin(ReportDatetimeModelFormMixin):
    """to be declared with FormValidators."""

    report_datetime_field_attr: str = "report_datetime"
