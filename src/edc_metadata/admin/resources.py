from import_export import resources

from ..models import CrfMetadata


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
            "close_datetime",
            "report_datetime",
            "document_user",
            "site__id",
            "created",
            "modified",
            "user_created",
            "user_modified",
        )
        export_order = fields
