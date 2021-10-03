from edc_metadata.stubs import RequisitionMetadataModelStub

from ...constants import NOT_REQUIRED, REQUIRED, REQUISITION
from ...requisition import RequisitionMetadataUpdater
from .updates_metadata_model_mixin import UpdatesMetadataModelMixin


class UpdatesRequisitionMetadataModelMixin(UpdatesMetadataModelMixin):
    """A model mixin used on Requisition models to enable them to
    update metadata upon save and delete.
    """

    metadata_updater_cls = RequisitionMetadataUpdater
    metadata_category = REQUISITION

    @property
    def metadata_updater(self: RequisitionMetadataModelStub) -> RequisitionMetadataUpdater:
        """Returns an instance of RequisitionMetadataUpdater."""
        opts = dict(
            visit_model_instance=self.visit,
            target_model=self._meta.label_lower,
            target_panel=self.panel,
        )
        return self.metadata_updater_cls(**opts)

    @property
    def metadata_query_options(self: RequisitionMetadataModelStub) -> dict:
        options = super().metadata_query_options
        options.update({"panel_name": self.panel.name})
        return options

    @property
    def metadata_default_entry_status(self: RequisitionMetadataModelStub) -> str:
        """Returns a string that represents the configured
        entry status of the requisition in the visit schedule.
        """
        requisitions_prn = self.metadata_visit_object.requisitions_prn
        if self.visit.visit_code_sequence != 0:
            requisitions = (
                self.metadata_visit_object.requisitions_unscheduled + requisitions_prn
            )
        else:
            requisitions = self.metadata_visit_object.requisitions + requisitions_prn
        requisition = [r for r in requisitions if r.panel.name == self.panel.name][0]
        return REQUIRED if requisition.required else NOT_REQUIRED

    class Meta:
        abstract = True
