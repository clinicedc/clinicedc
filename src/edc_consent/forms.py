from django import forms
from django.core.exceptions import ObjectDoesNotExist
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidatorMixin
from edc_registration.models import RegisteredSubject
from edc_sites.forms import SiteModelFormMixin

from .utils import get_reconsent_model_cls


class SubjectReconsentForm(
    SiteModelFormMixin, ActionItemFormMixin, FormValidatorMixin, forms.ModelForm
):
    def clean(self):
        cleaned_data = super().clean()
        try:
            RegisteredSubject.objects.get(
                subject_identifier=cleaned_data.get("subject_identifier"),
                identity=cleaned_data.get("identity"),
            )
        except ObjectDoesNotExist:
            raise forms.ValidationError({"identity": "Identity number does not match."})
        return cleaned_data

    class Meta:
        model = get_reconsent_model_cls()
        fields = "__all__"
        help_text = {"action_identifier": "(read-only)", "subject_identifier": "(read-only)"}
        widgets = {
            "action_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
            "subject_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
