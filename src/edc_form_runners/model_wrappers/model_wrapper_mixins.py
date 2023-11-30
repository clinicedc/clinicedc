from __future__ import annotations

from typing import TYPE_CHECKING

from ..utils import get_form_runner_issues

if TYPE_CHECKING:
    from edc_subject_model_wrappers import CrfModelWrapper


class FormRunnerModelWrapperMixin:
    @property
    def form_runner_issue_messages(self: CrfModelWrapper):
        qs = get_form_runner_issues(
            self.object._meta.label_lower,
            getattr(self.object, self.get_related_visit_model_attr()),
            panel_name=getattr(self, "panel_name", None),
        )
        messages = [f"{obj.message} [{obj.field_name}]" for obj in qs]
        return "<BR>".join(messages)
