from django import forms
from django.core.exceptions import ObjectDoesNotExist
from edc_sites.forms import SiteModelFormMixin

from .utils import get_registered_subject_model_cls


class ModelFormSubjectIdentifierMixin(SiteModelFormMixin):
    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
        help_text="(read-only)",
    )

    def clean(self):
        cleaned_data = super().clean()
        subject_identifier = cleaned_data.get("subject_identifier")
        try:
            get_registered_subject_model_cls().objects.get(
                subject_identifier=subject_identifier
            )
        except ObjectDoesNotExist:
            raise forms.ValidationError({"subject_identifier": "Invalid."})
        return cleaned_data
