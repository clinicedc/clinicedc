from django import forms

from ..exceptions import ActionError


class ActionItemModelFormMixin:
    def clean(self):
        cleaned_data = super().clean()
        action_cls = self._meta.model.get_action_cls()
        if self.action_cls:
            try:
                action_cls(
                    subject_identifier=self.subject_identifier,
                    action_identifier=self.action_identifier,
                    related_action_item=self.related_action_item,
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

    @property
    def action_identifier(self):
        action_identifier = self.cleaned_data.get("action_identifier")
        if not action_identifier:
            try:
                action_identifier = self.instance.action_identifier
            except AttributeError:
                action_identifier = None
        return action_identifier

    @property
    def related_action_item(self):
        related_action_item = self.cleaned_data.get("related_action_item")
        if not related_action_item:
            try:
                related_action_item = self.instance.related_action_item
            except AttributeError:
                related_action_item = None
        return related_action_item
