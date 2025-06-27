from django.contrib import admin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.html import format_html
from edc_model_admin.dashboard import ModelAdminDashboardMixin
from edc_model_admin.mixins import TemplatesModelAdminMixin
from edc_qareports.modeladmin_mixins import QaReportModelAdminMixin
from edc_sites.admin import SiteModelAdminMixin
from edc_utils import get_utcnow
from rangefilter.filters import DateRangeFilterBuilder, NumericRangeFilterBuilder

from ...admin_site import edc_pharmacy_admin
from ...analytics.dataframes.no_stock_for_subjects_df import stock_for_subjects_df
from ...models import StockAvailability
from ..list_filters import HasCodesListFilter


def wrap_html(s, url):
    return ",".join([f"<a href='{url}?q={c}'>{c}</a>" for c in s.split(",")])


def update_report(modeladmin, request):
    now = get_utcnow()
    modeladmin.model.objects.all().delete()

    df = stock_for_subjects_df()
    url = reverse("edc_pharmacy_admin:edc_pharmacy_storagebinitem_changelist")
    df.loc[~df["codes"].isna(), "codes"] = df.loc[~df["codes"].isna(), "codes"].apply(
        lambda s: wrap_html(s, url)
    )
    df.loc[df["codes"].isna(), "codes"] = None

    df.loc[~df["bins"].isna(), "bins"] = df.loc[~df["bins"].isna(), "bins"].apply(
        lambda s: wrap_html(s, url)
    )
    df.loc[df["bins"].isna(), "bins"] = None
    if not df.empty:
        data = [
            modeladmin.model(
                subject_identifier=row["subject_identifier"],
                site_id=row["site_id"],
                visit_code=row["visit_code"],
                appt_date=row["appt_date"],
                relative_days=row["relative_days"],
                codes=row["codes"],
                bins=row["bins"],
                report_model=modeladmin.model._meta.label_lower,
                created=now,
            )
            for _, row in df.iterrows()
        ]
        created = len(modeladmin.model.objects.bulk_create(data))
        # messages.success(request, "{} records were successfully created.".format(created))
        return created


@admin.register(StockAvailability, site=edc_pharmacy_admin)
class StockAvailabilityModelAdmin(
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
        "formatted_codes",
        "formatted_bins",
        "last_updated",
    ]

    list_filter = [
        HasCodesListFilter,
        ("appt_date", DateRangeFilterBuilder()),
        ("relative_days", NumericRangeFilterBuilder()),
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

    @admin.display(description="Codes", ordering="codes")
    def formatted_codes(self, obj):
        if obj.codes:
            return format_html(f'<span style="font-family:courier;">{obj.codes}</span>')
        return None

    @admin.display(description="Bins", ordering="bins")
    def formatted_bins(self, obj):
        if obj.codes:
            return format_html(f'<span style="font-family:courier;">{obj.bins}</span>')
        return None

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
