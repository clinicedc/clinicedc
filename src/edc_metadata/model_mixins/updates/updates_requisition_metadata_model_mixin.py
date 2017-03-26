from ...constants import REQUISITION

from .updates_metadata_model_mixin import UpdatesMetadataModelMixin


class UpdatesRequisitionMetadataModelMixin(UpdatesMetadataModelMixin):
    """A mixin used on Requisition models to enable them to
    update metadata upon update/delete.
    """

    @property
    def metadata_category(self):
        return REQUISITION

    @property
    def metadata_query_options(self):
        options = super().metadata_query_options
        options.update({'panel_name': self.panel_name})
        return options

    class Meta:
        abstract = True
