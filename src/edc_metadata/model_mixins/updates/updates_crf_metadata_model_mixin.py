from ...constants import CRF

from .updates_metadata_model_mixin import UpdatesMetadataModelMixin


class UpdatesCrfMetadataModelMixin(UpdatesMetadataModelMixin):
    """A mixin used on Crf models to enable them to
    update metadata upon update/delete."""

    @property
    def metadata_category(self):
        return CRF

    class Meta:
        abstract = True
