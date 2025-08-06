from django import forms

from ...models import Order, OrderItem


class OrderForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if (
            getattr(self.instance, "id", None)
            and OrderItem.objects.filter(
                order=self.instance, receiveitem__isnull=False
            ).exists()
        ):
            raise forms.ValidationError(
                "Order cannot be changed. Some items have been received"
            )
        return cleaned_data

    class Meta:
        model = Order
        fields = "__all__"
        help_text = {"order_identifier": "(read-only)"}
        widgets = {
            "order_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }


class OrderFormSuper(forms.ModelForm):

    class Meta:
        model = Order
        fields = "__all__"
        help_text = {"order_identifier": "(read-only)"}
        widgets = {
            "order_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
