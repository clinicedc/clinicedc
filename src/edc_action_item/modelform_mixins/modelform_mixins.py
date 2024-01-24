from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from ..exceptions import ActionError

if TYPE_CHECKING:
    from ..action import Action
    from ..models import ActionItem


class ActionItemModelFormMixin:
    def clean(self):
        cleaned_data = super().clean()
        action_cls = self._meta.model.get_action_cls()
        if self.action_cls:
            try:
                action_cls(
                    subject_identifier=self.get_subject_identifier(),
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
    def action_cls(self) -> Action:
        return self._meta.model.get_action_cls()

    @property
    def action_identifier(self) -> str:
        return self.cleaned_data.get("action_identifier") or getattr(
            self.instance, "action_identifier", None
        )

    @property
    def related_action_item(self) -> ActionItem:
        return self.cleaned_data.get("related_action_item") or getattr(
            self.instance, "related_action_item", None
        )
