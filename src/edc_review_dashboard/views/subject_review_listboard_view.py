from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db.models.aggregates import Count

from edc_appointment.view_mixins import AppointmentViewMixin
from edc_dashboard.url_names import url_names
from edc_dashboard.view_mixins import EdcViewMixin
from edc_listboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_listboard.views import ListboardView
from edc_metadata.view_mixins import MetadataViewMixin
from edc_navbar.view_mixin import NavbarViewMixin
from edc_subject_dashboard.view_mixins import (
    RegisteredSubjectViewMixin,
    SubjectVisitViewMixin,
)
from edc_visit_schedule.view_mixins import VisitScheduleViewMixin
from edc_visit_tracking.utils import get_related_visit_model

if TYPE_CHECKING:
    from edc_model.models import BaseUuidModel
    from edc_sites.model_mixins import SiteModelMixin
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    class RelatedVisitModel(SiteModelMixin, Base, BaseUuidModel):
        pass


class SubjectReviewListboardView(
    EdcViewMixin,
    NavbarViewMixin,
    MetadataViewMixin,
    AppointmentViewMixin,
    SubjectVisitViewMixin,
    VisitScheduleViewMixin,
    RegisteredSubjectViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    ListboardView,
):
    listboard_model = get_related_visit_model()
    navbar_selected = "subject_review"

    listboard_template = "subject_review_listboard_template"
    listboard_url = "subject_review_listboard_url"
    listboard_panel_style = "default"
    listboard_panel_title = "Subject Review"
    listboard_view_permission_codename = "edc_review_dashboard.view_subject_review_listboard"

    navbar_selected_item = "subject_review"
    ordering = ["subject_identifier", "visit_code", "visit_code_sequence"]
    paginate_by = 25
    search_form_url = "subject_review_listboard_url"
    search_fields = [
        "subject_identifier",
        "visit_code",
        "user_created",
        "user_modified",
    ]

    #  attr to call SubjectReviewListboardView.urls in urls.py
    urlconfig_getattr = "review_listboard_urls"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(
            subject_dashboard_url=url_names.get("subject_dashboard_url"),
        )
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.subject_identifier:
            queryset = (
                queryset.order_by("subject_identifier")
                .values("subject_identifier")
                .annotate(visit_count=Count("subject_identifier"))
            )
        return queryset
