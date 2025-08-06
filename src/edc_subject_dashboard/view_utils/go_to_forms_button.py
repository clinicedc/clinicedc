from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeVar

from django.utils.translation import gettext as _

from edc_appointment.constants import IN_PROGRESS_APPT
from edc_constants.constants import COMPLETE
from edc_view_utils import CHANGE, VIEW, NextQuerystring
from edc_visit_tracking.view_utils import RelatedVisitButton

if TYPE_CHECKING:
    from edc_visit_tracking.model_mixins import VisitModelMixin

    VisitModel = TypeVar("VisitModel", bound=VisitModelMixin)


__all__ = ["GotToFormsButton"]


@dataclass
class GotToFormsButton(RelatedVisitButton):
    """A button displayed on the subject dashboard of appointments
    that takes the user to the subject dashboard of CRFs and
    requisitions for the selected timepoint.
    """

    colors: tuple[str, str, str] = field(default=("primary", "primary", "default"))

    @property
    def label(self) -> str:
        return _("Forms")

    @property
    def title(self) -> str:
        return _("Go to CRFs and Requisitions")

    def color(self) -> str:
        """Shows as blue to direct user to go to the subject
        dashboard for this timepoint to edit CRFs and
        requisitions.

        Note:
            This button is relevant when the appointment is in
            progress. The related_visit document_status is set to
            COMPLETE when the related_visit is saved or re-saved.
            See also note on RelatedVisitButton.
        """
        color = self.colors[VIEW]
        if self.model_obj and self.appointment.appt_status == IN_PROGRESS_APPT:
            if self.model_obj.document_status == COMPLETE:
                color = self.colors[CHANGE]  # primary / blue
            else:
                color = self.colors[VIEW]  # default / grey
        return color

    @property
    def url(self) -> str:
        nq = NextQuerystring(
            next_url_name=self.next_url_name,
            reverse_kwargs=self.reverse_kwargs,
            extra_kwargs=self.extra_kwargs,
        )

        url = "?".join([f"{nq.next_url}", nq.querystring])
        return url

    @property
    def disabled(self) -> str:
        """Is only enabled if the appointment is set to
        IN_PROGRESS_APPT and the related_visit has been saved/resaved
        since appointment was set to IN PROGRESS.
        """
        disabled = "disabled"
        if (
            self.appointment.appt_status == IN_PROGRESS_APPT
            and self.model_obj.document_status == COMPLETE
            and any([self.perms.add, self.perms.change, self.perms.view])
        ):
            disabled = ""
        return disabled

    @property
    def label_fa_icon(self) -> str:
        if self.disabled:
            return ""
        return "fas fa-share"

    @property
    def fa_icon(self) -> str:
        return ""
