from ...constants import CRF
from ...metadata_updater import MetadataUpdater
from .updates_metadata_model_mixin import UpdatesMetadataModelMixin


class UpdatesCrfMetadataModelMixin(UpdatesMetadataModelMixin):
    """A model mixin used on CRF models to enable them to
    update `metadata` upon save and delete.
    """

    updater_cls = MetadataUpdater
    metadata_category = CRF

    class Meta:
        abstract = True
