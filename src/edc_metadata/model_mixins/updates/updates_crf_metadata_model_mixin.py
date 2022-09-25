from ...constants import CRF
from ...metadata_updater import MetadataUpdater
from .updates_metadata_model_mixin import UpdatesMetadataModelMixin


class UpdatesCrfMetadataModelMixin(UpdatesMetadataModelMixin):
    """A model mixin used on CRF models to enable them to
    update `metadata` upon save and delete.
    """

    metadata_updater_cls: MetadataUpdater = MetadataUpdater
    metadata_category: str = CRF

    class Meta:
        abstract = True
