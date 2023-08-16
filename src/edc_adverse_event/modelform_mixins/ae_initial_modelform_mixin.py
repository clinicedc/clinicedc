from django import forms
from django.conf import settings
from django.urls.base import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from edc_constants.constants import YES
from edc_reportable import GRADE4, GRADE5

from ..form_validators import AeInitialFormValidator
from ..utils import get_ae_model
from .ae_modelform_mixin import AeModelFormMixin


class AeInitialModelFormMixin(AeModelFormMixin):
    form_validator_cls = AeInitialFormValidator

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
        ae_followup_cls = get_ae_model("aefollowup")
        app_label = ae_followup_cls._meta.app_label
        model_name = ae_followup_cls._meta.object_name.lower()
        return reverse(
            f"{settings.ADVERSE_EVENT_ADMIN_SITE}:{app_label}_{model_name}_changelist"
        )

    def raise_if_followup_exists(self):
        """Raise an exception if the AE followup exists
        and the user is attempting to change this form.
        """
        ae_followup_cls = get_ae_model("aefollowup")
        if ae_followup_cls.objects.filter(ae_initial=self.instance.pk).exists():
            url = f"{self.changelist_url}?q={self.instance.action_identifier}"
            raise forms.ValidationError(
                format_html(  # nosec B703, B308
                    "Unable to save. Follow-up reports exist. Provide updates "
                    "to this report using the "
                    '{} instead. See <A href="{}">AE Follow-ups for {}</A>.',
                    ae_followup_cls._meta.verbose_name,
                    mark_safe(url),  # nosec B703, B308
                    mark_safe(self.instance),  # nosec B703, B308
                )
            )

    class Meta:
        help_texts = {"subject_identifier": "(read-only)", "action_identifier": "(read-only)"}
        widgets = {
            "subject_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
            "action_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
