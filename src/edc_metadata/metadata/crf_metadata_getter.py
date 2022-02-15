from .metadata_getter import MetadataGetter, MetadataValidator


class CrfMetadataValidator(MetadataValidator):
    pass


class CrfMetadataGetter(MetadataGetter):

    metadata_model = "edc_metadata.crfmetadata"

    metadata_validator_cls = CrfMetadataValidator
