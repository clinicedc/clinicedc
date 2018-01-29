from .constants import KEYED
from .target_handler import TargetHandler


class MetadataUpdaterError(Exception):
    pass


class MetadataUpdater:

    """A class to update a subject's metadata given
    the visit, target model name and desired entry status.
    """

    target_handler = TargetHandler

    def __init__(self, visit=None, target_model=None):
        self._metadata_obj = None
        self.visit = visit
        self.target_model = target_model

    def __repr__(self):
        return f'{self.__class__.__name__}(visit={self.visit})'

    def update(self, entry_status=None):

        if self.target.object:
            entry_status = KEYED
        metadata_obj = self.target.metadata_obj
        if entry_status and metadata_obj.entry_status != entry_status:
            metadata_obj.entry_status = entry_status
            metadata_obj.save()
        return metadata_obj

    @property
    def target(self):
        return self.target_handler(
            model=self.target_model,
            visit=self.visit)
