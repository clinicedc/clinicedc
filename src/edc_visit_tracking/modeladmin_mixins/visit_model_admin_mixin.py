from django.conf import settings
from django.contrib import admin
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from edc_model_admin.model_admin_audit_fields_mixin import (
    audit_fieldset_tuple,
    audit_fields,
)
from edc_visit_schedule.fieldsets import (
    visit_schedule_fieldset_tuple,
    visit_schedule_fields,
)


class VisitModelAdminMixin:

    """ModelAdmin subclass for models with a ForeignKey to
    'appointment', such as your visit model(s).

    In the child ModelAdmin class set the following attributes,
    for example:

        visit_attr = 'maternal_visit'
        dashboard_type = 'maternal'
    """

    date_hierarchy = "report_datetime"

    fieldsets = (
        (
            None,
            {
                "fields": [
                    "appointment",
                    "report_datetime",
                    "reason",
                    "reason_missed",
                    "reason_unscheduled",
                    "reason_unscheduled_other",
                    "info_source",
                    "info_source_other",
                    "comments",
                ]
            },
        ),
        visit_schedule_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "reason": admin.VERTICAL,
        "reason_unscheduled": admin.VERTICAL,
        "reason_missed": admin.VERTICAL,
        "info_source": admin.VERTICAL,
        "require_crfs": admin.VERTICAL,
    }

    list_display = [
        "appointment",
        "subject_identifier",
        "report_datetime",
        "reason",
        "study_status",
        "require_crfs",
        "created",
        "modified",
        "user_created",
        "user_modified",
    ]

    search_fields = [
        "id",
        "reason",
        "appointment__visit_code",
        "appointment__subject_identifier",
    ]

    list_filter = [
        "report_datetime",
        "appointment__visit_code",
        "appointment__visit_code_sequence",
        "reason",
        "require_crfs",
        "created",
        "modified",
        "user_created",
        "user_modified",
        "hostname_created",
    ]

    def subject_identifier(self, obj=None):
        return obj.appointment.subject_identifier

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get("using")
        if db_field.name == "appointment" and request.GET.get("appointment"):
            kwargs["queryset"] = db_field.related_model._default_manager.using(
                db
            ).filter(pk=request.GET.get("appointment"))
        else:
            kwargs["queryset"] = db_field.related_model._default_manager.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        fields = fields + audit_fields + visit_schedule_fields
        return fields

    def view_on_site(self, obj):
        dashboard_url_name = settings.DASHBOARD_URL_NAMES.get("subject_dashboard_url")
        try:
            return reverse(
                dashboard_url_name,
                kwargs=dict(
                    subject_identifier=obj.subject_identifier,
                    appointment=str(obj.appointment.id),
                ),
            )
        except NoReverseMatch:
            return super().view_on_site(obj)
