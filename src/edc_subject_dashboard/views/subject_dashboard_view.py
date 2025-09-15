from __future__ import annotations

from typing import Any

from django.core.exceptions import ImproperlyConfigured

from edc_action_item.view_mixins import ActionItemViewMixin
from edc_appointment.view_mixins import AppointmentViewMixin
from edc_consent.view_mixins import ConsentViewMixin
from edc_dashboard.view_mixins import EdcViewMixin
from edc_dashboard.views import DashboardView
from edc_data_manager.view_mixins import DataManagerViewMixin
from edc_locator.view_mixins import SubjectLocatorViewMixin
from edc_metadata.view_mixins import MetadataViewMixin
from edc_navbar.view_mixin import NavbarViewMixin
from edc_sites.site import sites
from edc_visit_schedule.view_mixins import VisitScheduleViewMixin

from ..view_mixins import RegisteredSubjectViewMixin, SubjectVisitViewMixin


class VerifyRequisitionMixin:
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        scanning = self.kwargs.get("scanning")
        kwargs.update(scanning=scanning)
        return super().get_context_data(**kwargs)


class SubjectDashboardView(
    EdcViewMixin,
    NavbarViewMixin,
    VisitScheduleViewMixin,
    MetadataViewMixin,
    ConsentViewMixin,
    SubjectLocatorViewMixin,
    ActionItemViewMixin,
    DataManagerViewMixin,
    SubjectVisitViewMixin,
    AppointmentViewMixin,
    RegisteredSubjectViewMixin,
    VerifyRequisitionMixin,
    DashboardView,
):
    navbar_selected_item = "consented_subject"

    dashboard_url_name = "subject_dashboard_url"
    dashboard_template = "subject_dashboard_template"

    default_manager = "on_site"

    def __init__(self, **kwargs):
        if not self.navbar_name:
            raise ImproperlyConfigured(f"'navbar_name' cannot be None. See {self!r}.")
        super().__init__(**kwargs)

    @property
    def manager(self) -> str:
        """Returns the name of the model manager"""
        if sites.user_may_view_other_sites(self.request):
            return "objects"
        return self.default_manager
