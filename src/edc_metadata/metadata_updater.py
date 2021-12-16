from typing import Optional, Type

from django.db import models

from .constants import KEYED
from .target_handler import TargetHandler


class MetadataUpdaterError(Exception):
    pass


class MetadataUpdater:
    """A class to update a subject's metadata given
    the visit_model_instance, target model name and desired entry status.
    """

    target_handler = TargetHandler

    def __init__(self, visit_model_instance=None, target_model=None):
        self._metadata_obj = None
        self.visit_model_instance = visit_model_instance
        self.target_model = target_model
        # self._missed_visit_model_instance = None

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(visit_model_instance={self.visit_model_instance}, "
            f"target_model={self.target_model})"
        )

    def update(self, entry_status: Optional[str] = None) -> Type[models.Model]:
        metadata_obj = self.target.metadata_obj
        if self.target.object:
            entry_status = KEYED
        # if not metadata_obj and self.missed_visit_model_instance:
        #     pass
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
        return self.target_handler(
            model=self.target_model, visit_model_instance=self.visit_model_instance
        )

    # def missed_visit_model_instance(self):
    #     if not self._missed_visit_model_instance:
    #         try:
    #             self._missed_visit_model_instance = (
    #                 get_subject_visit_missed_model_cls().objects.get(
    #                     subject_visit=self.visit_model_instance
    #                 )
    #             )
    #         except ObjectDoesNotExist:
    #             self._missed_visit_model_instance = None
    #     return self._missed_visit_model_instance
