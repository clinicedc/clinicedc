from django import forms
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from edc_action_item.forms import ActionItemFormMixin
from edc_constants.constants import YES
from edc_form_validators import FormValidatorMixin
from edc_registration.modelform_mixins import ModelFormSubjectIdentifierMixin
from edc_reportable import GRADE4, GRADE5

from ..form_validators import AeInitialFormValidator


class AeInitialForm(
    FormValidatorMixin,
    ModelFormSubjectIdentifierMixin,
    ActionItemFormMixin,
    forms.ModelForm,
):

    ae_followup_model_cls = None
    ae_admin_site_name = None

    form_validator_cls = AeInitialFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        self.raise_if_followup_exists()
        self.validate_sae_and_grade()
        return cleaned_data

    def validate_sae_and_grade(self):
        """Raise an exception if grade>=4 and user did not
        indicate that this is an SAE.
        """
        if (
            self.cleaned_data.get("ae_grade") in [GRADE4, GRADE5]
            and self.cleaned_data.get("sae") != YES
        ):
            raise forms.ValidationError({"sae": "Invalid. Grade is >= 4"})

    @property
    def changelist_url(self):
        app_label = self.ae_followup_model_cls._meta.app_label
        model_name = self.ae_followup_model_cls._meta.object_name.lower()
        return reverse(f"{self.ae_admin_site_name}:{app_label}_{model_name}_changelist")

    def raise_if_followup_exists(self):
        """Raise an exception if the AE followup exists
        and the user is attempting to change this form.
        """

        if self.ae_followup_model_cls.objects.filter(
            ae_initial=self.instance.pk
        ).exists():
            url = f"{self.changelist_url}?q={self.instance.action_identifier}"
            raise forms.ValidationError(
                mark_safe(
                    f"Unable to save. Follow-up reports exist. Provide updates "
                    f"to this report using the "
                    f"{self.ae_followup_model_cls._meta.verbose_name} instead. "
                    f'See <A href="{url}">AE Follow-ups for {self.instance}</A>.'
                )
            )
