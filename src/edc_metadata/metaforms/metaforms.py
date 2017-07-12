from .metaform import MetaformError


class Metaforms:

    """A class that generates a collection of metaform objects, e.g. CRF
    or REQUISITION, from a queryset of metadata objects.

    See classes Crf, Requisition in edc_visit_schedule.
    """

    metadata_getter_cls = None
    metaform_cls = None

    def __init__(self, **kwargs):
        self.metadata = self.metadata_getter_cls(**kwargs)
        self.objects = []
        if self.metadata.visit:
            for metadata_obj in self.metadata.metadata_objects:
                try:
                    metaform = self.metaform_cls(
                        metadata_obj=metadata_obj,
                        visit=self.metadata.visit,
                        **metadata_obj.__dict__)
                except MetaformError:
                    pass
                else:
                    self.objects.append(metaform)
