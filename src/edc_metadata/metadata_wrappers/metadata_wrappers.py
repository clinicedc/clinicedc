from __future__ import annotations

from django.core.management.color import color_style

from ..metadata import MetadataGetter
from .metadata_wrapper import MetadataWrapper

style = color_style()


class MetadataWrappers:

    """A class that generates a collection of MetadataWrapper objects, e.g. CRF
    or REQUISITION, from a queryset of metadata objects.

    See also classes Crf, Requisition in edc_visit_schedule.
    """

    metadata_getter_cls: MetadataGetter = MetadataGetter
    metadata_wrapper_cls: MetadataWrapper = MetadataWrapper

    def __init__(self, **kwargs) -> None:
        metadata_getter = self.metadata_getter_cls(**kwargs)
        self.objects = []
        if metadata_getter.related_visit:
            for metadata_obj in metadata_getter.metadata_objects:
                metadata_wrapper = self.metadata_wrapper_cls(
                    metadata_obj=metadata_obj,
                    visit=metadata_getter.related_visit,
                )
                self.objects.append(metadata_wrapper)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.objects})"
