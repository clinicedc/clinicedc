from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.utils import timezone

from edc_dashboard.view_mixins import EdcViewMixin
from edc_listboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_listboard.views import ListboardView as BaseListboardView
from edc_navbar import NavbarViewMixin

from ...constants import (
    AE_FOLLOWUP_ACTION,
    AE_TMG_ACTION,
    DEATH_REPORT_ACTION,
    DEATH_REPORT_TMG_ACTION,
)
from ...utils import get_adverse_event_app_label

if TYPE_CHECKING:
    from django.db.models import Q


class SummaryListboardView(
    NavbarViewMixin,
    EdcViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    BaseListboardView,
):
    listboard_back_url = "tmg_home_url"

    ae_tmg_model = f"{get_adverse_event_app_label()}.aetmg"
    listboard_template = "tmg_summary_listboard_template"
    listboard_url = "tmg_summary_listboard_url"
    listboard_panel_style = "warning"
    listboard_model = "edc_action_item.actionitem"
    listboard_panel_title = "TMG: Events Summary"
    listboard_view_permission_codename = "edc_adverse_event.view_tmg_listboard"

    navbar_selected_item = "tmg_home"
    ordering = "-report_datetime"
    paginate_by = 25
    search_form_url = "tmg_summary_listboard_url"
    action_type_names = [
        AE_TMG_ACTION,
        DEATH_REPORT_TMG_ACTION,
        DEATH_REPORT_ACTION,
        AE_FOLLOWUP_ACTION,
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
        kwargs.update(AE_TMG_ACTION=AE_TMG_ACTION, utc_date=timezone.now().date())
        return super().get_context_data(**kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        q_object, options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update({"action_type__name__in": self.action_type_names})
        return q_object, options
