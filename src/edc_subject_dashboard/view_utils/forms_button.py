from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeVar

from edc_appointment.constants import IN_PROGRESS_APPT
from edc_constants.constants import COMPLETE

from .model_button import CHANGE, VIEW
from .next_dashboard_url import NextDashboardUrl
from .related_visit_button import RelatedVisitButton

if TYPE_CHECKING:
    from edc_visit_tracking.model_mixins import VisitModelMixin

    VisitModel = TypeVar("VisitModel", bound=VisitModelMixin)


__all__ = ["FormsButton"]


@dataclass
class FormsButton(RelatedVisitButton):
    """A button displayed on the subject dashboard of appointments
    that takes the user to the subject dashboard of CRFs and
    requisitions for the selected timepoint.
    """

    labels: tuple[str, str, str] = field(default=3 * ("Forms",))
    btn_colors: tuple[str, str, str] = field(
        default=("btn-primary", "btn-primary", "btn-default")
    )
    titles: tuple[str, str, str] = field(default=3 * ("Go to CRFs and Requisitions",))

    def btn_color(self) -> str:
        """Shows as blue to direct user to go to the subject
        dashboard for this timepoint to edit CRFs and
        requisitions.

        Note:
            This button is relevant when the appointment is in
            progress. The related_visit document_status is set to
            COMPLETE when the related_visit is saved or re-saved.
            See also note on RelatedVisitButton.
        """
        btn_color = self.btn_colors[VIEW]
        if self.model_obj and self.appointment.appt_status == IN_PROGRESS_APPT:
            if self.model_obj.document_status == COMPLETE:
                btn_color = self.btn_colors[CHANGE]  # primary / blue
            else:
                btn_color = self.btn_colors[VIEW]  # default / grey
        return btn_color

    @property
    def url(self) -> str:
        dashboard_url = NextDashboardUrl(
            dashboard_url_name=self.dashboard_url_name,
            reverse_kwargs=self.reverse_kwargs,
            extra_kwargs=self.extra_kwargs,
        )

        url = "?".join([f"{dashboard_url.url}", dashboard_url.querystring])
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
        fa_icon = super().fa_icons
        if self.disabled:
            fa_icon = ""
        return fa_icon
