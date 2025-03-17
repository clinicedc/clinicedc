from django.contrib import admin
from django.db.models import QuerySet
from edc_model_admin.dashboard import ModelAdminDashboardMixin
from edc_model_admin.mixins import TemplatesModelAdminMixin
from edc_qareports.modeladmin_mixins import QaReportModelAdminMixin
from edc_sites.admin import SiteModelAdminMixin
from edc_utils import get_utcnow
from rangefilter.filters import DateRangeFilterBuilder

from ...admin_site import edc_pharmacy_admin
from ...analytics import no_stock_for_subjects_df
from ...models import StockOut


def update_report(modeladmin, request):
    now = get_utcnow()
    modeladmin.model.objects.all().delete()
    df = no_stock_for_subjects_df()
    if not df.empty:
        data = [
            modeladmin.model(
                subject_identifier=row["subject_identifier"],
                site_id=row["site_id"],
                visit_code=row["visit_code"],
                appt_date=row["appt_date"],
                relative_days=row["relative_days"],
                report_model=modeladmin.model._meta.label_lower,
                created=now,
            )
            for _, row in df.iterrows()
        ]
        created = len(modeladmin.model.objects.bulk_create(data))
        # messages.success(request, "{} records were successfully created.".format(created))
        return created


@admin.register(StockOut, site=edc_pharmacy_admin)
class StockOutModelAdmin(
    QaReportModelAdminMixin,
    SiteModelAdminMixin,
    ModelAdminDashboardMixin,
    TemplatesModelAdminMixin,
    admin.ModelAdmin,
):
    queryset_filter: dict | None = None
    qa_report_list_display_insert_pos = 3
    include_note_column = False
    ordering = ["relative_days"]
    list_display = [
        "dashboard",
        "subject",
        "site",
        "visit_code",
        "appt_date",
        "relative_days",
        "last_updated",
    ]

    list_filter = [
        ("appt_date", DateRangeFilterBuilder()),
        "visit_code",
        "site_id",
    ]

    search_fields = ["subject_identifier"]

    def get_queryset(self, request) -> QuerySet:
        update_report(self, request)

        qs = super().get_queryset(request)
        if self.queryset_filter:
            qs = qs.filter(**self.queryset_filter)
        return qs

    @admin.display(description="subject", ordering="subject_identifier")
    def subject(self, obj=None):
        return obj.subject_identifier

    @admin.display(description="visit", ordering="visit_code")
    def visit(self, obj=None):
        return obj.visit_code

    @admin.display(description="last_updated", ordering="created")
    def last_updated(self, obj=None):
        return obj.created

    def get_view_only_site_ids_for_user(self, request) -> list[int]:
        return [s.id for s in request.user.userprofile.sites.all() if s.id != request.site.id]
