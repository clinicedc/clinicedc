from __future__ import annotations

from .metadata_getter import MetadataGetter, MetadataValidator


class RequisitionMetadataValidator(MetadataValidator):
    @property
    def extra_query_attrs(self) -> dict:
        return dict(panel__name=self.metadata_obj.panel_name)


class RequisitionMetadataGetter(MetadataGetter):
    metadata_model = "edc_metadata.requisitionmetadata"

    metadata_validator_cls = RequisitionMetadataValidator
