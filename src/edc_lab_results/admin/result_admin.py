from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilterBuilder

from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..admin_site import edc_lab_results_admin
from ..models import Result


@admin.register(Result, site=edc_lab_results_admin)
class ResultAdmin(
    ModelAdminSubjectDashboardMixin, admin.ModelAdmin
):
    list_display = (
        "subject_identifier",
        "screening_identifier",
        "dashboard",
        "visit_code",
        "investigation",
        "link_to_reportable",
        "result_value",
        "units",
        "flag",
        "subject_not_found",
        "requisition_ambiguous",
        "order_datetime",
        "report_datetime",
        "order_no",
        "sample_no",
        "result_no",
    )
    list_filter = (
        "subject_not_found",
        "requisition_ambiguous",
        ("report_datetime", DateRangeFilterBuilder()),
        ("order_datetime", DateRangeFilterBuilder()),
        "visit_code",
        "investigation",
        "utest_id",
        "report_type",
        "flag",
    )
    search_fields = (
        "subject_identifier",
        "screening_identifier",
        "name_id",
        "investigation",
        "order_no",
        "sample_no",
        "result_no",
    )
    ordering = ("-report_datetime",)

    @admin.display(description="UTESTID", ordering="utest_id")
    def link_to_reportable(self, obj):
        if obj.utest_id:
            url = reverse(
                "edc_reportable_admin:"
                "edc_reportable_normaldata_changelist"
            )
            return format_html(
                '<A href="{url}?q={utestid}">{utestid}</A>',
                url=url,
                utestid=obj.utest_id,
            )
        return None
