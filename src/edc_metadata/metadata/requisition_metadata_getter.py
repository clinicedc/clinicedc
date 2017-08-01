from ..models import RequisitionMetadata
from .metadata_getter import MetadataGetter


class RequisitionMetadataGetter(MetadataGetter):

    metadata_model_cls = RequisitionMetadata
