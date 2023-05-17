from ..metadata import CrfMetadataGetter
from .crf_metadata_wrapper import CrfMetadataWrapper
from .metadata_wrappers import MetadataWrappers


class CrfMetadataWrappers(MetadataWrappers):
    metadata_getter_cls = CrfMetadataGetter
    metadata_wrapper_cls = CrfMetadataWrapper
