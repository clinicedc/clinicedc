from django.core.exceptions import ObjectDoesNotExist

from .metadata import Creator


class MetadataHandlerError(Exception):
    pass


class MetadataHandler:

    """A class to get or create a CRF metadata model instance.
    """

    creator_cls = Creator

    def __init__(self, metadata_model=None, visit=None, model=None):
        self.metadata_model = metadata_model
        self.model = model
        self.visit = visit
        self.creator = self.creator_cls(visit=self.visit, update_keyed=True)

    def get_or_create(self):
        """Returns a metadata model instance.
        """
        try:
            metadata_obj = self.metadata_model.objects.get(
                **self.query_options)
        except ObjectDoesNotExist:
            metadata_obj = self._create()
        return metadata_obj

    def _create(self):
        """Returns a new metadata model instance for this CRF.
        """
        crf_object = [
            crf for crf in self.creator.visit.crfs if crf.model == self.model][0]
        return self.creator.create_crf(crf_object)

    @property
    def query_options(self):
        """Returns a dict of options to query the metadata model.
        """
        query_options = self.visit.metadata_query_options
        query_options.update({
            'model': self.model,
            'subject_identifier': self.visit.subject_identifier})
        return query_options
