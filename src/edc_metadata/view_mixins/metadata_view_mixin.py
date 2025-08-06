from __future__ import annotations

from edc_appointment.utils import update_appt_status_for_timepoint

from ..constants import KEYED, NOT_REQUIRED, REQUIRED
from ..utils import (
    get_crf_metadata,
    get_requisition_metadata,
    refresh_metadata_for_timepoint,
)


class MetadataViewError(Exception):
    pass


class MetadataViewMixin:
    panel_model: str = "edc_lab.panel"
    metadata_show_status: list[str] = [REQUIRED, KEYED]

    def get_context_data(self, **kwargs) -> dict:
        if self.appointment:
            # always refresh metadata / run rules
            refresh_metadata_for_timepoint(self.appointment, allow_create=True)
            referer = self.request.headers.get("Referer")
            if referer and "subject_review_listboard" in referer:
                if self.appointment.related_visit:
                    update_appt_status_for_timepoint(self.appointment.related_visit)
            crf_qs = self.get_crf_metadata()
            requisition_qs = self.get_requisition_metadata()
            kwargs.update(crfs=crf_qs, requisitions=requisition_qs)
        kwargs.update(
            NOT_REQUIRED=NOT_REQUIRED,
            REQUIRED=REQUIRED,
            KEYED=KEYED,
        )
        return super().get_context_data(**kwargs)

    def get_crf_metadata(self):
        return (
            get_crf_metadata(self.appointment)
            .filter(entry_status__in=self.metadata_show_status)
            .order_by("show_order")
        )

    def get_requisition_metadata(self):
        return (
            get_requisition_metadata(self.appointment)
            .filter(entry_status__in=self.metadata_show_status)
            .order_by("show_order")
        )
