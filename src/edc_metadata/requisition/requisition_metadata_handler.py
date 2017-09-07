from ..metadata_handler import MetadataHandler


class RequisitionMetadataHandler(MetadataHandler):

    """A class to get or create a requisition metadata
    model instance.
    """

    def __init__(self, panel=None, **kwargs):
        super().__init__(**kwargs)
        self.panel = panel

    def _create(self):
        """Returns a created metadata model instance for
        this requisition.
        """
        requisition_object = [
            r for r in self.creator.visit.requisitions
            if r.panel.name == self.panel][0]
        return self.creator.create_requisition(requisition_object)

    @property
    def query_options(self):
        """Returns a dict of options to query the metadata model.
        """
        query_options = self.visit.metadata_query_options
        query_options.update({
            'model': self.model,
            'panel_name': self.panel,
            'subject_identifier': self.visit.subject_identifier,
            'visit_code': self.visit.visit_code})
        return query_options
