from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps

from .constants import CRF, KEYED
from .metadata_handler import MetadataHandler

if TYPE_CHECKING:
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    from .model_mixins.creates import CreatesMetadataModelMixin
    from .models import CrfMetadata, RequisitionMetadata

    class RelatedVisitModel(CreatesMetadataModelMixin, Base):
        pass


class MetadataUpdaterError(Exception):
    pass


class MetadataUpdater:
    """A class to update a subject's metadata given
    the related_visit, target model name and desired entry status.
    """

    metadata_handler_cls: Type[MetadataHandler] = MetadataHandler
    metadata_category: str = CRF
    metadata_model: str = "edc_metadata.crfmetadata"

    def __init__(
        self,
        related_visit: RelatedVisitModel = None,
        target_model: str = None,
        allow_create: bool | None = None,
    ):
        self._metadata_obj: CrfMetadata | RequisitionMetadata | None = None
        self.allow_create = True if allow_create is None else allow_create
        self.related_visit = related_visit
        self.target_model = target_model

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(related_visit={self.related_visit}, "
            f"target_model={self.target_model})"
        )

    def get_and_update(self, entry_status: str = None) -> CrfMetadata | RequisitionMetadata:
        metadata_obj = self.metadata_handler.metadata_obj
        if entry_status != KEYED and self.is_keyed(metadata_obj.model):
            entry_status = KEYED
        if metadata_obj.entry_status != entry_status:
            metadata_obj.entry_status = entry_status
            metadata_obj.save(update_fields=["entry_status"])
            metadata_obj.refresh_from_db()
            if metadata_obj.entry_status != entry_status:
                raise MetadataUpdaterError(
                    "Expected entry status does not match `entry_status` on "
                    "metadata model instance. "
                    f"Got {entry_status} != {metadata_obj.entry_status}."
                )
        return metadata_obj

    def is_keyed(self, model: str) -> bool:
        """Returns True if source model exists."""
        return (
            django_apps.get_model(model)
            .objects.filter(subject_visit=self.related_visit)
            .exists()
        )

    @property
    def metadata_handler(self) -> MetadataHandler:
        return self.metadata_handler_cls(
            metadata_model=self.metadata_model,
            model=self.target_model,
            related_visit=self.related_visit,
            allow_create=self.allow_create,
        )
