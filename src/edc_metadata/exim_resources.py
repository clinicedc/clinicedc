from import_export.resources import ModelResource

from .models import CrfMetadata, RequisitionMetadata


class CrfMetadataResource(ModelResource):
    class Meta:
        model = CrfMetadata


class RequisitionMetadataResource(ModelResource):
    class Meta:
        model = RequisitionMetadata
