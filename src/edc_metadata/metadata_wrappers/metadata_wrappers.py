from typing import ClassVar

from django.core.management.color import color_style

from ..stubs import MetadataGetterStub, MetadataWrapperStub

style = color_style()


class MetadataWrappers:

    """A class that generates a collection of MetadataWrapper objects, e.g. CRF
    or REQUISITION, from a queryset of metadata objects.

    See also classes Crf, Requisition in edc_visit_schedule.
    """

    metadata_getter_cls: ClassVar[MetadataGetterStub] = None
    metadata_wrapper_cls: ClassVar[MetadataWrapperStub] = None

    def __init__(self, **kwargs):
        metadata_getter = self.metadata_getter_cls(**kwargs)
        self.objects = []
        if metadata_getter.visit_model_instance:
            for metadata_obj in metadata_getter.metadata_objects:
                metadata_wrapper = self.metadata_wrapper_cls(
                    metadata_obj=metadata_obj,
                    visit=metadata_getter.visit_model_instance,
                )
                self.objects.append(metadata_wrapper)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.objects})"
