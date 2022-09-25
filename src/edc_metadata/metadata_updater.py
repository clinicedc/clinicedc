from __future__ import annotations

from typing import Type

from django.db import models

from .constants import KEYED
from .target_handler import TargetHandler


class MetadataUpdaterError(Exception):
    pass


class MetadataUpdater:
    """A class to update a subject's metadata given
    the related_visit, target model name and desired entry status.
    """

    target_handler = TargetHandler

    def __init__(self, related_visit=None, target_model=None):
        self._metadata_obj = None
        self.related_visit = related_visit
        self.target_model = target_model

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(related_visit={self.related_visit}, "
            f"target_model={self.target_model})"
        )

    def update(self, entry_status: str = None) -> Type[models.Model]:
        metadata_obj = self.target.metadata_obj
        if self.target.object:
            entry_status = KEYED
        if entry_status and metadata_obj.entry_status != entry_status:
            metadata_obj.entry_status = entry_status
            metadata_obj.save()
            metadata_obj.refresh_from_db()
            if metadata_obj.entry_status != entry_status:
                raise MetadataUpdaterError(
                    "Expected entry status does not match `entry_status` on "
                    "metadata model instance. "
                    f"Got {entry_status} != {metadata_obj.entry_status}."
                )
        return metadata_obj

    @property
    def target(self):
        return self.target_handler(model=self.target_model, related_visit=self.related_visit)
