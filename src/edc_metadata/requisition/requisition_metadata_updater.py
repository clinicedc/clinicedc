from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..constants import REQUISITION
from ..metadata_updater import MetadataUpdater
from .requisition_metadata_handler import RequisitionMetadataHandler

if TYPE_CHECKING:
    from edc_lab.models import Panel


class RequisitionMetadataError(Exception):
    pass


class RequisitionMetadataUpdater(MetadataUpdater):
    """A class to update a subject's requisition metadata given
    the visit, target model name, panel and desired entry status.
    """

    metadata_handler_cls: RequisitionMetadataHandler = RequisitionMetadataHandler
    metadata_category: str = REQUISITION
    metadata_model: str = "edc_metadata.requisitionmetadata"

    def __init__(self, source_panel: Panel = None, **kwargs):
        super().__init__(**kwargs)
        self.source_panel = source_panel

    @property
    def metadata_handler(self):
        return self.metadata_handler_cls(
            metadata_model=self.metadata_model,
            model=self.source_model,
            related_visit=self.related_visit,
            panel=self.source_panel,
            allow_create=self.allow_create,
        )

    @property
    def source_model_options(self) -> dict[str, Any]:
        """Returns a dictionary of query options to filter for, or
        get, the SubjectRequisition model instance.
        """
        return dict(subject_visit_id=self.related_visit.id, panel__name=self.source_panel.name)
