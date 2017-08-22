from django.core.exceptions import ObjectDoesNotExist

from ..metadata_updater import MetadataUpdater
from .requisition_target_handler import RequisitionTargetHandler


class RequisitionMetadataError(Exception):
    pass


class RequisitionMetadataUpdater(MetadataUpdater):

    """A class to update a subject's requisition metadata given
    the visit, target model name and desired entry status.
    """
    target_handler = RequisitionTargetHandler

    def update(self, target_model=None, target_panel=None, entry_status=None):
        metadata_obj = None
        self.target = self.target_handler(
            model=target_model, visit=self.visit,
            target_panel=target_panel,
            metadata_category=self.metadata_category)
        if entry_status and not self.target.object:
            options = self.visit.metadata_query_options
            options.update({
                'model': target_model,
                'panel_name': target_panel,
                'subject_identifier': self.visit.subject_identifier,
                'visit_code': self.visit.visit_code})
            try:
                metadata_obj = self.target.metadata_model.objects.get(
                    **options)
            except ObjectDoesNotExist as e:
                raise RequisitionMetadataError(
                    f'Metadata does not exist for {target_model}.{target_panel}. '
                    f'Check your rule. Got {e}. Options={options}.')
            metadata_obj.entry_status = entry_status
            metadata_obj.save()
        return metadata_obj
