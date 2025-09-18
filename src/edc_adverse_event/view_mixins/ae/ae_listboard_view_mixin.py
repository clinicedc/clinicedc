from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from edc_constants.constants import CLOSED, NEW, OPEN
from edc_dashboard.view_mixins import EdcViewMixin
from edc_listboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_listboard.views import ListboardView as BaseListboardView
from edc_navbar import NavbarViewMixin

from ...constants import AE_INITIAL_ACTION
from ...pdf_reports import AePdfReport
from ...utils import get_ae_model

if TYPE_CHECKING:
    from django.db.models import Q, QuerySet


class AeListboardViewMixin(
    NavbarViewMixin,
    EdcViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    BaseListboardView,
):
    pdf_report_cls = AePdfReport

    listboard_back_url = "ae_home_url"
    home_url = "ae_home_url"
    listboard_panel_title = "Adverse Events: AE Initial and Follow-up Reports"

    listboard_template = "ae_listboard_template"
    listboard_url = "ae_listboard_url"
    listboard_panel_style = "default"
    listboard_model = "edc_action_item.actionitem"
    listboard_view_permission_codename = "edc_adverse_event.view_ae_listboard"

    listboard_instructions = format_html(
        "{}",
        mark_safe(render_to_string("edc_adverse_event/ae/ae_listboard_instructions.html")),  # nosec B703 B308,
    )
    navbar_selected_item = "ae_home"
    ordering = "-report_datetime"
    paginate_by = 25
    search_form_url = "ae_listboard_url"
    action_type_names = [AE_INITIAL_ACTION]

    search_fields = [
        "subject_identifier",
        "action_identifier",
        "parent_action_item__action_identifier",
        "related_action_item__action_identifier",
        "user_created",
        "user_modified",
    ]

    @property
    def ae_initial_model_cls(self):
        return get_ae_model("aeinitial")

    def get(self, request, *args, **kwargs):
        response = None
        if request.GET.get("pdf"):
            response = self.print_pdf_report(
                action_identifier=self.request.GET.get("pdf"),
                request=request,
            )
        return response or super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(
            AE_INITIAL_ACTION=AE_INITIAL_ACTION,
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

    def get_updated_queryset(self, queryset) -> QuerySet:
        pks = []
        for obj in queryset:
            try:
                obj.reference_obj
            except ObjectDoesNotExist:
                pks.append(obj.pk)
        return queryset.exclude(pk__in=pks)

    def print_pdf_report(self, action_identifier=None, request=None):
        try:
            ae_initial_obj = self.ae_initial_model_cls.objects.get(
                action_identifier=action_identifier
            )
        except ObjectDoesNotExist:
            pass
        else:
            pdf_report = self.get_pdf_report(
                ae_initial=ae_initial_obj,
                subject_identifier=ae_initial_obj.subject_identifier,
                user=self.request.user,
                request=request,
            )
            return pdf_report.render_to_response()
        return None

    def get_pdf_report(self, **kwargs) -> AePdfReport:
        pdf_report_cls = getattr(self.ae_initial_model_cls, "pdf_report_cls", None)
        if not pdf_report_cls:
            pdf_report_cls = getattr(self, "pdf_report_cls", None)
        return pdf_report_cls(**kwargs)
