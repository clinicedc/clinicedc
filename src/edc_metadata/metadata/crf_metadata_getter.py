from ..models import CrfMetadata
from .metadata_getter import MetadataGetter


class CrfMetadataGetter(MetadataGetter):

    metadata_model_cls = CrfMetadata
