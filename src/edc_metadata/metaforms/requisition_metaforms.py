from ..metadata import RequisitionMetadataGetter
from .metaforms import Metaforms
from .requisition_metaform import RequisitionMetaform


class RequisitionMetaforms(Metaforms):

    metadata_getter_cls = RequisitionMetadataGetter
    metaform_cls = RequisitionMetaform
