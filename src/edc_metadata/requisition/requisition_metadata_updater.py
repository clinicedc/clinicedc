from __future__ import annotations

from typing import TYPE_CHECKING

from ..metadata_updater import MetadataUpdater
from .requisition_target_handler import RequisitionTargetHandler

if TYPE_CHECKING:
    from edc_lab.models import Panel


class RequisitionMetadataError(Exception):
    pass


class RequisitionMetadataUpdater(MetadataUpdater):

    """A class to update a subject's requisition metadata given
    the visit, target model name, panel and desired entry status.
    """

    target_handler: RequisitionTargetHandler = RequisitionTargetHandler

    def __init__(self, target_panel: Panel = None, **kwargs):
        super().__init__(**kwargs)
        self.target_panel = target_panel

    @property
    def target(self):
        target = self.target_handler(
            model=self.target_model,
            related_visit=self.related_visit,
            target_panel=self.target_panel,
        )
        return target
