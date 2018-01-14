from .metadata_wrapper import MetadataWrapper


class RequisitionMetadataWrapper(MetadataWrapper):

    label = 'Requisition'

    def __init__(self, metadata_obj=None, **kwargs):
        self.panel_name = metadata_obj.panel_name
        super().__init__(metadata_obj=metadata_obj, **kwargs)

    @property
    def options(self):
        options = super().options
        options.update(panel__name=self.panel_name)
        return options
