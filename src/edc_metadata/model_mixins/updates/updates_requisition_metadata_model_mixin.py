from ...constants import REQUISITION
from ...requisition import RequisitionMetadataUpdater
from .updates_metadata_model_mixin import UpdatesMetadataModelMixin
from edc_metadata.constants import REQUIRED, NOT_REQUIRED


class UpdatesRequisitionMetadataModelMixin(UpdatesMetadataModelMixin):
    """A mixin used on Requisition models to enable them to
    update metadata upon update/delete.
    """

    updater_cls = RequisitionMetadataUpdater
    metadata_category = REQUISITION

    @property
    def metadata_updater(self):
        """Returns an instance of RequisitionMetadataUpdater.
        """
        return self.updater_cls(
            visit=self.visit,
            target_model=self._meta.label_lower,
            target_panel=self.panel_name)

    @property
    def metadata_query_options(self):
        options = super().metadata_query_options
        options.update({'panel_name': self.panel_name})
        return options

    @property
    def metadata_default_entry_status(self):
        """Returns a string that represents the configured entry status
        of the requisition in the visit schedule.
        """
        if self.visit.visit_code_sequence != 0:
            requisitions = self.metadata_visit_object.requisitions_unscheduled
        else:
            requisitions = self.metadata_visit_object.requisitions
        requisition = [r for r in requisitions
                       if r.panel.name == self.panel_name][0]
        return REQUIRED if requisition.required else NOT_REQUIRED

    class Meta:
        abstract = True
