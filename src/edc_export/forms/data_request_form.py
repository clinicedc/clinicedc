from django import forms
from django.apps import apps as django_apps
from edc_form_validators import FormValidator, FormValidatorMixin

from ..models import DataRequest


class DataRequestFormValidator(FormValidator):

    pass


class DataRequestForm(FormValidatorMixin, forms.ModelForm):

    form_validator_cls = DataRequestFormValidator

    def clean(self):
        cleaned_data = super().clean()
        if self.cleaned_data.get("requested"):
            requested = self.cleaned_data.get("requested").split("\n")
            requested = [x.strip() for x in requested if x.strip()]
            for model in requested:
                try:
                    django_apps.get_model(model)
                except (LookupError, ValueError):
                    raise forms.ValidationError(f"Invalid model. Got '{model}'")
        return cleaned_data

    class Meta:
        model = DataRequest
        fields = "__all__"
