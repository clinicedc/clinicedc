from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from edc_constants.constants import OTHER
from edc_dashboard.url_names import url_names
from edc_form_validators import FormValidator, FormValidatorMixin
from edc_registration.models import RegisteredSubject
from edc_screening.utils import get_subject_screening_model_cls

from .models import SubjectRefusal


class SubjectRefusalFormValidator(FormValidator):
    def clean(self):
        self.required_if(OTHER, field="reason", field_required="other_reason")


class ScreeningFormMixin:
    def clean(self):
        cleaned_data = super().clean()
        screening_identifier = cleaned_data.get("screening_identifier")
        if screening_identifier:
            subject_screening = get_subject_screening_model_cls().objects.get(
                screening_identifier=screening_identifier
            )
            if not subject_screening.eligible:
                url_name = url_names.get("screening_listboard_url")
                url = reverse(
                    url_name,
                    kwargs={"screening_identifier": self.instance.screening_identifier},
                )
                msg = mark_safe(
                    "Not allowed. Subject is not eligible. "
                    f'See subject <A href="{url}?q={screening_identifier}">'
                    f"{screening_identifier}</A>"
                )
                raise forms.ValidationError(msg)
        return cleaned_data


class AlreadyConsentedFormMixin:
    def clean(self):
        cleaned_data = super().clean()
        try:
            obj = RegisteredSubject.objects.get(
                screening_identifier=self.instance.screening_identifier
            )
        except ObjectDoesNotExist:
            pass
        else:
            url_name = url_names.get("subject_dashboard_url")
            url = reverse(
                url_name,
                kwargs={"subject_identifier": obj.subject_identifier},
            )
            msg = mark_safe(
                "Not allowed. Subject has already consented. "
                f'See subject <A href="{url}">{obj.subject_identifier}</A>'
            )
            raise forms.ValidationError(msg)
        return cleaned_data


class SubjectRefusalForm(
    AlreadyConsentedFormMixin, ScreeningFormMixin, FormValidatorMixin, forms.ModelForm
):
    form_validator_cls = SubjectRefusalFormValidator

    screening_identifier = forms.CharField(
        label="Screening identifier",
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = SubjectRefusal
        fields = "__all__"
