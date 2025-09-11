from django import forms
from django.apps import apps as django_apps

from edc_constants.constants import CANCELLED, NEW, OPEN
from edc_model_form.mixins import BaseModelFormMixin

from ..models import ActionItem


class ActionItemForm(BaseModelFormMixin, forms.ModelForm):
    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        self.force_open_status()
        self.raise_if_cannot_cancel()
        return cleaned_data

    def force_open_status(self) -> None:
        """Sets status to open for edited NEW action items."""
        if self.instance.id and self.cleaned_data.get("status") == NEW:
            self.cleaned_data["status"] = OPEN

    def raise_if_cannot_cancel(self) -> None:
        if (
            self.instance.id
            and self.cleaned_data.get("status") == CANCELLED
            and django_apps.get_model(self.instance.reference_model)
            .objects.filter(action_identifier=self.instance.action_identifier)
            .exists()
        ):
            raise forms.ValidationError({"status": "Invalid. This action cannot be cancelled"})

    class Meta:
        model = ActionItem
        fields = "__all__"
