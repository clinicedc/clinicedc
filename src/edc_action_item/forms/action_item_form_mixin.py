from django import forms


class ActionItemFormMixin:

    """Declare with forms.ModelForm."""

    class Meta:
        help_text = {"action_identifier": "(read-only)"}
        widgets = {"action_identifier": forms.TextInput(attrs={"readonly": "readonly"})}
