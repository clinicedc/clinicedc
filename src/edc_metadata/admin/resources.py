from import_export import resources

from ..models import CrfMetadata, RequisitionMetadata


class CrfMetadataResource(resources.ModelResource):
    """Resource used by django-import-export to export the CrfMetadata
    changelist to Excel/CSV.

    Exports whatever queryset the changelist is currently showing, so
    filters/search/ordering apply.
    """

    class Meta:
        model = CrfMetadata
        fields = (
            "subject_identifier",
            "visit_schedule_name",
            "schedule_name",
            "visit_code",
            "visit_code_sequence",
            "model",
            "document_name",
            "entry_status",
            "show_order",
            "due_datetime",
            "fill_datetime",
            "document_user",
            "site__id",
            "created",
            "modified",
            "user_created",
            "user_modified",
        )
        export_order = fields


class RequisitionMetadataResource(resources.ModelResource):
    """Resource used by django-import-export to export the
    RequisitionMetadata changelist to Excel/CSV.

    Exports whatever queryset the changelist is currently showing, so
    filters/search/ordering apply.
    """

    class Meta:
        model = RequisitionMetadata
        fields = (
            "subject_identifier",
            "visit_schedule_name",
            "schedule_name",
            "visit_code",
            "visit_code_sequence",
            "model",
            "panel_name",
            "document_name",
            "entry_status",
            "show_order",
            "due_datetime",
            "fill_datetime",
            "document_user",
            "site__id",
            "created",
            "modified",
            "user_created",
            "user_modified",
        )
        export_order = fields
