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
        if (
            cleaned_data.get("container")
            and cleaned_data.get("container") == cleaned_data.get("from_stock").container
        ):
            raise forms.ValidationError(
                {"container": "Stock is already packed in this container."}
            )
        if (
            cleaned_data.get("container")
            and cleaned_data.get("container").qty
            > cleaned_data.get("from_stock").container.qty
        ):
            raise forms.ValidationError({"container": "Cannot pack into larger container."})
        if cleaned_data.get("requested_qty") and self.instance.processed_qty:
            if cleaned_data.get("requested_qty") < self.instance.processed_qty:
                raise forms.ValidationError(
                    {"requested_qty": "Cannot be less than the number of containers processed"}
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
