from .target_handler import TargetHandler


class MetadataUpdater:

    """A class to update a visit's metadata given the target model name and
    desired entry status.
    """

    target_handler = TargetHandler

    def __init__(self, visit=None):
        self.visit = visit

    def update(self, target_model=None, entry_status=None):
        metadata_obj = None
        self.target = self.target_handler(
            model=target_model, visit=self.visit)
        if self.may_update_metadata and entry_status:
            options = self.visit.metadata_query_options
            options.update({
                'model': target_model,
                'subject_identifier': self.visit.subject_identifier})
            options.update(**self.additional_metadata_options)

            metadata_obj = self.target.metadata_model.objects.get(**options)
            metadata_obj.entry_status = entry_status
            metadata_obj.save()
        return metadata_obj

    @property
    def may_update_metadata(self):
        """Update metadata if the target model "model instance"
        does not exist.
        """
        return not self.target.object

    @property
    def additional_metadata_options(self):
        """Returns additional options to "get" the metadata instance.
        """
        return {}
