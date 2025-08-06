from typing import Any

from django.urls import reverse
from django.views.generic import TemplateView

from edc_dashboard.url_names import url_names
from edc_dashboard.view_mixins import EdcViewMixin, UrlRequestContextMixin
from edc_navbar import NavbarViewMixin

from ..utils import get_adverse_event_admin_site, get_adverse_event_app_label


class AeHomeView(UrlRequestContextMixin, EdcViewMixin, NavbarViewMixin, TemplateView):
    ae_listboard_url = "ae_listboard_url"
    death_report_listboard_url = "death_report_listboard_url"
    navbar_selected_item = "ae_home"
    template_name = "edc_adverse_event/ae/ae_home.html"
    url_name = "ae_home_url"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        app_list_url = f"{get_adverse_event_admin_site()}:app_list"
        ae_initial_changelist_url = reverse(
            f"{get_adverse_event_admin_site()}:{get_adverse_event_app_label()}_"
            f"aeinitial_changelist"
        )
        death_report_changelist_url = reverse(
            f"{get_adverse_event_admin_site()}:{get_adverse_event_app_label()}_"
            f"deathreport_changelist"
        )
        ae_listboard_url = url_names.get(self.ae_listboard_url)
        death_report_listboard_url = url_names.get(self.death_report_listboard_url)
        kwargs.update(
            ADVERSE_EVENT_ADMIN_SITE=get_adverse_event_admin_site(),
            ADVERSE_EVENT_APP_LABEL=get_adverse_event_app_label(),
            app_list_url=app_list_url,
            ae_listboard_url=ae_listboard_url,
            ae_initial_changelist_url=ae_initial_changelist_url,
            death_report_changelist_url=death_report_changelist_url,
            death_report_listboard_url=death_report_listboard_url,
            **self.add_url_to_context(new_key="ae_home_url", existing_key=self.url_name),
        )
        return super().get_context_data(**kwargs)
