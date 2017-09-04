from django.core.exceptions import ObjectDoesNotExist

from .target_handler import TargetHandler


class MetadataUpdaterError(Exception):
    pass


class MetadataUpdater:

    """A class to update a subject's metadata given
    the visit, target model name and desired entry status.
    """

    target_handler = TargetHandler

    def __init__(self, visit=None, metadata_category=None):
        self.metadata_category = metadata_category
        self.visit = visit

    def __repr__(self):
        return f'{self.__class__.__name__}(visit={self.visit})'

    def update(self, target_model=None, entry_status=None):
        metadata_obj = None
        self.target = self.target_handler(
            model=target_model,
            visit=self.visit,
            metadata_category=self.metadata_category)
        if entry_status and not self.target.object:
            options = self.visit.metadata_query_options
            options.update({
                'model': target_model,
                'subject_identifier': self.visit.subject_identifier})
            try:
                metadata_obj = self.target.metadata_model.objects.get(
                    **options)
            except ObjectDoesNotExist as e:
                raise MetadataUpdaterError(
                    f'{e}.. for target model \'{target_model}\' with options {options}')
            if metadata_obj.entry_status != entry_status:
                metadata_obj.entry_status = entry_status
                metadata_obj.save()
        return metadata_obj
