from .metadata_wrapper import DeletedInvalidMetadata


class MetadataWrappers:

    """A class that generates a collection of MetadataWrapper objects, e.g. CRF
    or REQUISITION, from a queryset of metadata objects.

    See classes Crf, Requisition in edc_visit_schedule.
    """

    metadata_getter_cls = None
    metadata_wrapper_cls = None

    def __init__(self, **kwargs):
        self.metadata = self.metadata_getter_cls(**kwargs)
        self.objects = []
        if self.metadata.visit:
            for metadata_obj in self.metadata.metadata_objects:
                try:
                    metadata_wrapper = self.metadata_wrapper_cls(
                        metadata_obj=metadata_obj,
                        visit=self.metadata.visit,
                        **metadata_obj.__dict__)
                except DeletedInvalidMetadata:
                    pass
                else:
                    self.objects.append(metadata_wrapper)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.objects})'
