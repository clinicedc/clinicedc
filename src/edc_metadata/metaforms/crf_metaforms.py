from ..metadata import CrfMetadataGetter
from .crf_metaform import CrfMetaform
from .metaforms import Metaforms


class CrfMetaforms(Metaforms):

    metadata_getter_cls = CrfMetadataGetter
    metaform_cls = CrfMetaform
