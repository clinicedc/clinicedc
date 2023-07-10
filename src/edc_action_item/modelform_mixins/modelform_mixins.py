from django import forms

from ..exceptions import ActionError


class ActionItemModelFormMixin:
    def clean(self):
        cleaned_data = super().clean()
        action_cls = self._meta.model.get_action_cls()
        if self.action_cls:
            try:
                action_cls(
                    subject_identifier=cleaned_data.get("subject_identifier"),
                    action_identifier=cleaned_data.get("action_identifier"),
                    related_action_item=cleaned_data.get("related_action_item"),
                    readonly=True,
                )
            except ActionError as e:
                raise forms.ValidationError(
                    f"{str(e.message)}. Please contact your data manager."
                )
        return cleaned_data

    @property
    def action_cls(self):
        try:
            action_cls = self._meta.model.get_action_cls()
        except AttributeError:
            action_cls = None
        return action_cls
