from django import forms

from ...models import Container


class ContainerForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("max_per_subject") and not cleaned_data.get("may_request_as"):
            raise forms.ValidationError(
                {"max_per_subject": "Not applicable. Leave blank or 0"}
            )
        if not cleaned_data.get("max_per_subject") and cleaned_data.get("may_request_as"):
            raise forms.ValidationError({"max_per_subject": "This field is required"})
        if (
            cleaned_data.get("max_per_subject")
            and cleaned_data.get("max_per_subject") > 6
            and cleaned_data.get("may_request_as")
        ):
            raise forms.ValidationError({"max_per_subject": "May not exceed 6"})
        return cleaned_data

    class Meta:
        model = Container
        fields = "__all__"
