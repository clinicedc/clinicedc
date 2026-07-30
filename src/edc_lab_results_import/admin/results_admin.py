from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilterBuilder

from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..admin_site import edc_lab_results_import_admin
from ..models import Result


@admin.register(Result, site=edc_lab_results_import_admin)
class ResultAdmin(ModelAdminSubjectDashboardMixin, admin.ModelAdmin):
    list_display = (
        "subject_identifier",
        "screening_identifier",
        "dashboard",
        "order_no",
        "order_datetime",
        "visit_code",
        "visit_code_sequence",
        "requisition_identifier",
        "requisition",
        "source_utestid",
        "result_value",
        "units",
        "flag",
        "result_status",
        "link_to_reportable",
        "order_no",
        "sample_no",
        "result_no",
    )
    list_filter = (
        ("report_datetime", DateRangeFilterBuilder()),
        ("order_datetime", DateRangeFilterBuilder()),
        "visit_code",
        "visit_code_sequence",
        "report_type",
        "result_status",
        "flag",
    )
    search_fields = (
        "subject_identifier",
        "screening_identifier",
        "name_id",
        "source_utestid",
        "order_no",
        "sample_no",
        "result_no",
        "requisition_identifier",
    )
    ordering = ("-report_datetime",)

    @admin.display(description="UTESTID", ordering="utestid")
    def link_to_reportable(self, obj):
        if obj.utestid:
            url = reverse("edc_reportable_admin:edc_reportable_normaldata_changelist")
            return format_html(
                '<A href="{url}?q={utestid}">{utestid}</A>',
                url=url,
                utestid=obj.utestid,
            )
        return None
