from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db.models import Min
from django.utils import timezone

from edc_constants.constants import CLOSED, NEW, OPEN
from edc_dashboard.view_mixins import EdcViewMixin
from edc_listboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_listboard.views import ListboardView as BaseListboardView
from edc_navbar import NavbarViewMixin
from edc_navbar.get_default_navbar import get_default_navbar

from ...constants import (
    AE_TMG_ACTION,
    DEATH_REPORT_TMG_ACTION,
    DEATH_REPORT_TMG_SECOND_ACTION,
)
from ...utils import get_adverse_event_app_label, has_valid_tmg_perms

if TYPE_CHECKING:
    from django.db.models import Q


class Qs:
    def __init__(self, subject_identifier, report_datetime):
        self.subject_identifier = subject_identifier
        self.report_datetime = report_datetime


class TmgAeListboardViewMixin(
    NavbarViewMixin,
    EdcViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    BaseListboardView,
):
    listboard_back_url = "tmg_home_url"

    ae_tmg_model = f"{get_adverse_event_app_label()}.aetmg"
    listboard_template = "tmg_ae_listboard_template"
    listboard_url = "tmg_ae_listboard_url"
    listboard_panel_style = "warning"
    listboard_model = "edc_action_item.actionitem"
    listboard_panel_title = "TMG: AE Reports"
    listboard_view_permission_codename = "edc_adverse_event.view_tmg_listboard"

    navbar_name = get_default_navbar()
    navbar_selected_item = "tmg_home"
    ordering = "-report_datetime"
    paginate_by = 10
    search_form_url = "tmg_ae_listboard_url"
    action_type_names = [
        AE_TMG_ACTION,
        DEATH_REPORT_TMG_ACTION,
        DEATH_REPORT_TMG_SECOND_ACTION,
    ]

    search_fields = [
        "subject_identifier",
        "action_identifier",
        "parent_action_item__action_identifier",
        "related_action_item__action_identifier",
        "user_created",
        "user_modified",
    ]

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(
            AE_TMG_ACTION=AE_TMG_ACTION,
            utc_date=timezone.now().date(),
            subject_identifier=self.kwargs.get("subject_identifier"),
        )
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return [
            Qs(
                obj.get("subject_identifier"),
                obj.get("report_datetime"),
            )
            for obj in queryset.values("subject_identifier").annotate(
                report_datetime=Min("report_datetime"),
            )
        ]

    def get_queryset_filter_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        q_object, options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(
            action_type__name__in=self.action_type_names,
            status__in=[NEW, OPEN, CLOSED],
        )
        if kwargs.get("subject_identifier"):
            options.update({"subject_identifier": kwargs.get("subject_identifier")})
        return q_object, options


class StatusTmgAeListboardView(TmgAeListboardViewMixin):
    status = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        has_valid_tmg_perms(self.request, add_message=True)
        kwargs.update(status=self.status)
        return super().get_context_data(**kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        q_object, options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update({"status": self.status})
        return q_object, options
