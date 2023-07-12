from django import forms

from ..utils import TotalDaysMismatch, validate_total_days


class DrugSupplyNcdModelFormMixin:
    list_model_cls = None

    def clean(self):
        cleaned_data = super().clean()
        data = dict(self.data.lists())
        rx = self.list_model_cls.objects.filter(id__in=data.get("rx") or [])
        rx_names = [obj.display_name for obj in rx]
        inline_drug_names = self.raise_on_duplicates()

        if data.get("rx_days")[0] is not None and data.get("rx_days")[0] != "":
            try:
                validate_total_days(self, rx_days=int(data.get("rx_days")[0]))
            except TotalDaysMismatch as e:
                raise forms.ValidationError(e)

        if (
            self.cleaned_data.get("drug")
            and self.cleaned_data.get("drug").display_name not in rx_names
        ):
            treatment = " + ".join(rx_names)
            raise forms.ValidationError(
                f"Invalid. `{self.cleaned_data.get('drug').display_name}` "
                f"not in current treatment of `{treatment}`"
            )

        self.raise_on_missing_drug(rx_names, inline_drug_names)

        return cleaned_data

    def raise_on_duplicates(self):
        drug_names = []
        total_forms = self.data.get(f"{self.relation_label}_set-TOTAL_FORMS")
        for form_index in range(0, int(total_forms or 0)):
            inline_rx_id = self.data.get(f"{self.relation_label}_set-{form_index}-drug")
            if inline_rx_id:
                rx_obj = self.list_model_cls.objects.get(id=int(inline_rx_id))
                if rx_obj.display_name in drug_names:
                    raise forms.ValidationError("Invalid. Duplicates not allowed")
                drug_names.append(rx_obj.display_name)
        return drug_names

    @staticmethod
    def raise_on_missing_drug(rx_names, inline_drug_names):
        for display_name in rx_names:
            if display_name not in inline_drug_names:
                raise forms.ValidationError(f"Missing drug. Also expected {display_name}.")
