from __future__ import annotations

from typing import Type

from .metadata_getter import MetadataGetter, MetadataValidator


class CrfMetadataValidator(MetadataValidator):
    pass


class CrfMetadataGetter(MetadataGetter):
    metadata_model: str = "edc_metadata.crfmetadata"

    metadata_validator_cls: Type[CrfMetadataValidator] = CrfMetadataValidator
