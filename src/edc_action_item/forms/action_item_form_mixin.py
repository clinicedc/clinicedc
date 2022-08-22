from django import forms


class ActionItemFormMixin:

    """Declare with forms.ModelForm."""

    class Meta:
        help_text = {"subject_identifier": "(read-only)", "action_identifier": "(read-only)"}
        widgets = {
            "subject_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
            "action_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }


class ActionItemCrfFormMixin:

    """Declare with forms.ModelForm."""

    class Meta:
        help_text = {"action_identifier": "(read-only)"}
        widgets = {
            "action_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
