from ...constants import CRF

from .updates_metadata_model_mixin import UpdatesMetadataModelMixin


class UpdatesCrfMetadataModelMixin(UpdatesMetadataModelMixin):
    """A mixin used on Crf models to enable them to
    update metadata upon update/delete."""

    @property
    def metadata_category(self):
        return CRF

    def run_metadata_rules_for_crf(self):
        """Runs all the rule groups for this app label.

        Gets called in the signal.
        """
        self.visit.run_metadata_rules(visit=self.visit)

    class Meta:
        abstract = True
