from __future__ import annotations

from typing import TYPE_CHECKING

from .metadata_wrapper import MetadataWrapper

if TYPE_CHECKING:
    from ..models import RequisitionMetadata


class RequisitionMetadataWrapper(MetadataWrapper):
    label = "Requisition"

    def __init__(self, metadata_obj: RequisitionMetadata = None, **kwargs) -> None:
        self.panel_name = metadata_obj.panel_name
        super().__init__(metadata_obj=metadata_obj, **kwargs)

    @property
    def options(self) -> dict:
        options = super().options
        options.update(panel__name=self.panel_name)
        return options

    @property
    def html_id(self) -> str:
        return f"id_{self.panel_name}"
