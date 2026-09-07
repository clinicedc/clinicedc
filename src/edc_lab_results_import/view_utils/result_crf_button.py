from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from edc_subject_dashboard.view_utils import CrfButton

__all__ = ["ResultCrfButton"]


@dataclass
class ResultCrfButton(CrfButton):
    """An add/change button for the result CRF of an imported result.

    Unlike a button on the subject dashboard, `next` returns to the
    result search page for this subject, so `reverse_kwargs` is narrowed
    to `subject_identifier`. The result search url takes no
    `appointment`, and `NextQuerystring` reverses eagerly.

    Where the search that produced this button was narrowed by a
    requisition identifier, that is carried back too, so the user
    returns to the search they left rather than to every result for the
    subject.

    The related visit is passed to the changeform in the querystring by
    `CrfButton.extra_kwargs`. Here the requisition is passed as well, so
    both FKs are prepopulated on the add form.

    `group_key` identifies the result set this button was built for.
    See `ResultSearchView.get_group_key`.
    """

    requisition_id: UUID | None = None
    requisition_identifier: str = ""
    group_key: str = ""
    next_url_name: str = field(default="result_search_url")

    @property
    def reverse_kwargs(self) -> dict[str, str]:
        reverse_kwargs = dict(subject_identifier=self.appointment.subject_identifier)
        if self.requisition_identifier:
            reverse_kwargs.update(requisition_identifier=self.requisition_identifier)
        return reverse_kwargs

    @property
    def extra_kwargs(self) -> dict[str, str | int | UUID]:
        extra_kwargs = super().extra_kwargs
        if self.requisition_id:
            extra_kwargs.update(requisition=str(self.requisition_id))
        return extra_kwargs
