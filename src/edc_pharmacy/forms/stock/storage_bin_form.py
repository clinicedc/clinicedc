from django import forms

from ...models import StorageBin, StorageBinItem


class StorageBinForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("capacity") is not None:
            item_count = StorageBinItem.objects.filter(
                storage_bin__bin_identifier=cleaned_data.get("bin_identifier")
            ).count()
            if item_count > 0 and cleaned_data.get("capacity") < item_count:
                raise forms.ValidationError(
                    {
                        "capacity": (
                            "Cannot be less than the number of items in bin. "
                            f"(Got {item_count})"
                        )
                    }
                )
        return cleaned_data

    class Meta:
        model = StorageBin
        fields = "__all__"
