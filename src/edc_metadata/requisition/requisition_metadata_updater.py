from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps

from .. import REQUISITION
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

    def __init__(self, target_panel: Panel = None, **kwargs):
        super().__init__(**kwargs)
        self.target_panel = target_panel

    @property
    def metadata_handler(self):
        return self.metadata_handler_cls(
            metadata_model=self.metadata_model,
            model=self.target_model,
            related_visit=self.related_visit,
            panel=self.target_panel,
            allow_create=self.allow_create,
        )

    def is_keyed(self, model: str) -> bool:
        """Returns True if source model exists."""
        return (
            django_apps.get_model(model)
            .objects.filter(
                subject_visit=self.related_visit, panel__name=self.target_panel.name
            )
            .exists()
        )
