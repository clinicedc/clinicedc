class CrfMetadataAdminMixin:
    def seq(self, obj=None):
        return obj.visit_code_sequence

    def get_subject_dashboard_url_kwargs(self, obj):
        return dict(
            subject_identifier=obj.subject_identifier,
            visit_schedule_name=obj.visit_schedule_name,
            schedule_name=obj.schedule_name,
            visit_code=obj.visit_code,
        )

    search_fields = ("subject_identifier", "model", "id")
    list_display = (
        "subject_identifier",
        "dashboard",
        "model",
        "visit_code",
        "seq",
        "entry_status",
        "fill_datetime",
        "due_datetime",
        "close_datetime",
        "created",
        "hostname_created",
    )
    list_filter = (
        "entry_status",
        "visit_code",
        "visit_code_sequence",
        "schedule_name",
        "visit_schedule_name",
        "model",
        "fill_datetime",
        "created",
        "user_created",
        "hostname_created",
    )
    readonly_fields = (
        "subject_identifier",
        "model",
        "visit_code",
        "schedule_name",
        "visit_schedule_name",
        "show_order",
        "current_entry_title",
    )
