import re

from django import forms
from edc_form_validators import FormValidator

from ..models import Box


class BoxForm(forms.ModelForm):
    def clean(self) -> dict:
        cleaned_data = super().clean()
        form_validator = FormValidator(cleaned_data=cleaned_data)
        if cleaned_data.get("specimen_types"):
            pattern = "([0-9][0-9]*[ ]*,[ ]*)*[0-9][0-9]*"
            match = re.match(pattern, cleaned_data.get("specimen_types"))
            if not match:
                raise forms.ValidationError(
                    {"specimen_types": "Invalid list of specimen types."},
                    code="invalid format",
                )
            elif match.group() != cleaned_data.get("specimen_types"):
                raise forms.ValidationError(
                    {"specimen_types": "Invalid list of specimen types."},
                    code="invalid format",
                )
            else:
                specimen_types = [code.strip() for code in match.group().split(",")]
                if len(specimen_types) != len(list(set(specimen_types))):
                    raise forms.ValidationError(
                        {"specimen_types": "List must be unique."},
                        code="list not unique",
                    )
            cleaned_data["specimen_types"] = ",".join(specimen_types)
        form_validator.validate_other_specify("category")
        return cleaned_data

    class Meta:
        fields = "__all__"
        model = Box
