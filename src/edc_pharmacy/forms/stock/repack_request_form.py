from django import forms

from ...models import RepackRequest


class RepackRequestForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("from_stock") and not cleaned_data.get("from_stock").confirmed:
            raise forms.ValidationError(
                {
                    "from_stock": (
                        "Unconfirmed stock item. Only confirmed "
                        "stock items may be used to repack"
                    )
                }
            )
        return cleaned_data

    class Meta:
        model = RepackRequest
        fields = "__all__"
        help_text = {
            "repack_identifier": "(read-only)",
        }
        widgets = {
            "repack_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
