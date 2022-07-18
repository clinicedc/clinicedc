from django import forms
from edc_constants.constants import NEW, OPEN

from ..models import ActionItem


class ActionItemForm(forms.ModelForm):

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        self.force_open_status()
        return cleaned_data

    def force_open_status(self):
        """Sets status to open for edited NEW action items."""
        if self.instance.id and self.cleaned_data.get("status") == NEW:
            self.cleaned_data["status"] = OPEN

    class Meta:
        model = ActionItem
        fields = "__all__"
