from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from edc_constants.constants import CLOSED, NEW, OPEN
from edc_dashboard.view_mixins import EdcViewMixin
from edc_listboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_listboard.views import ListboardView as BaseListboardView
from edc_navbar import NavbarViewMixin

from ...constants import DEATH_REPORT_ACTION
from ...pdf_reports import DeathPdfReport
from ...utils import get_ae_model

if TYPE_CHECKING:
    from django.db.models import Q


class DeathReportListboardViewMixin(
    NavbarViewMixin,
    EdcViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    BaseListboardView,
):
    listboard_back_url = "ae_home_url"
    home_url = "ae_home_url"
    pdf_report_cls = DeathPdfReport

    listboard_template = "ae_death_report_listboard_template"
    listboard_url = "death_report_listboard_url"
    listboard_panel_style = "default"
    listboard_model = "edc_action_item.actionitem"
    listboard_panel_title = "Adverse Events: Death Reports"
    listboard_view_permission_codename = "edc_adverse_event.view_ae_listboard"
    listboard_instructions = format_html(
        "{}",
        mark_safe("edc_adverse_event/ae/death_report_listboard_instructions.html"),  # nosec B703 B308
    )

    navbar_selected_item = "ae_home"
    ordering = "-report_datetime"
    paginate_by = 25
    search_form_url = "death_report_listboard_url"
    action_type_names = (DEATH_REPORT_ACTION,)

    search_fields = (
        "subject_identifier",
        "action_identifier",
        "parent_action_item__action_identifier",
        "related_action_item__action_identifier",
        "user_created",
        "user_modified",
    )

    def get(self, request, *args, **kwargs):
        if request.GET.get("pdf"):
            response = self.print_pdf_report(
                action_identifier=self.request.GET.get("pdf"), request=request
            )
            return response
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(
            DEATH_REPORT_ACTION=DEATH_REPORT_ACTION,
            utc_date=timezone.now().date(),
            **self.add_url_to_context(
                new_key="ae_home_url",
                existing_key=self.home_url,
            ),
        )
        return super().get_context_data(**kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        q_object, options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(
            action_type__name__in=self.action_type_names,
            status__in=[NEW, OPEN, CLOSED],
        )
        if kwargs.get("subject_identifier"):
            options.update({"subject_identifier": kwargs.get("subject_identifier")})
        return q_object, options

    @property
    def death_report_model_cls(self):
        return get_ae_model("deathreport")

    def print_pdf_report(self, action_identifier=None, request=None):
        try:
            death_report_obj = self.death_report_model_cls.objects.get(
                action_identifier=action_identifier
            )
        except ObjectDoesNotExist:
            pass
        else:
            pdf_report = self.get_pdf_report(
                pk=death_report_obj.id,
                user=self.request.user,
                request=request,
            )
            return pdf_report.render_to_response()
        return None

    def get_pdf_report(self, **kwargs) -> DeathPdfReport:
        pdf_report_cls = getattr(self.death_report_model_cls, "pdf_report_cls", None)
        if not pdf_report_cls:
            pdf_report_cls = getattr(self, "pdf_report_cls", None)
        return pdf_report_cls(**kwargs)
