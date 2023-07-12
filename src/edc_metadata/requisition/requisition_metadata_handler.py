from __future__ import annotations

from typing import TYPE_CHECKING

from edc_visit_tracking.constants import MISSED_VISIT

from ..metadata_handler import MetadataHandler, MetadataHandlerError

if TYPE_CHECKING:
    from edc_lab.models import Panel

    from ..models import RequisitionMetadata


class RequisitionMetadataHandler(MetadataHandler):

    """A class to get or create a requisition metadata
    model instance.
    """

    def __init__(self, panel: Panel = None, **kwargs):
        super().__init__(**kwargs)
        self.panel = panel

    def _create(self, exception_msg: str | None = None) -> RequisitionMetadata:
        """Returns a created RequisitionMetadata model instance for this
        requisition.
        """
        metadata_obj = None
        try:
            requisition_object = [
                requisition
                for requisition in self.creator.visit.all_requisitions
                if requisition.panel.name == self.panel.name
            ][0]
        except IndexError as e:
            if self.related_visit.reason != MISSED_VISIT:
                raise MetadataHandlerError(
                    f"Model not found. Not in visit.all_crfs. Model {self.model}. Got {e}"
                )
        else:
            metadata_obj = self.creator.create_requisition(requisition_object)
        return metadata_obj

    @property
    def query_options(self) -> dict:
        """Returns a dict of options to query the metadata model."""
        query_options = super().query_options
        query_options.update({"panel_name": self.panel.name})
        return query_options
