from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from django.db.models import Q
from django.db.models.aggregates import Count
from edc_appointment.view_mixins import AppointmentViewMixin
from edc_dashboard.view_mixins import EdcViewMixin
from edc_listboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_listboard.views import ListboardView
from edc_metadata.constants import KEYED, REQUIRED
from edc_metadata.view_mixins import MetadataViewMixin
from edc_navbar.view_mixin import NavbarViewMixin
from edc_sites.site import sites
from edc_subject_dashboard.view_mixins import (
    RegisteredSubjectViewMixin,
    SubjectVisitViewMixin,
)
from edc_subject_model_wrappers import RelatedVisitModelWrapper
from edc_visit_schedule.view_mixins import VisitScheduleViewMixin
from edc_visit_tracking.utils import get_related_visit_model_cls

if TYPE_CHECKING:
    from edc_model.models import BaseUuidModel
    from edc_sites.model_mixins import SiteModelMixin
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    class RelatedVisitModel(SiteModelMixin, Base, BaseUuidModel):
        pass


@dataclass(order=True)
class Row:
    subject_identifier: str = field(compare=True)
    visit_count: int = field(compare=False)


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
    listboard_model = get_related_visit_model_cls()
    navbar_selected = "subject_review"

    listboard_template = "subject_review_listboard_template"
    listboard_url = "subject_review_listboard_url"
    listboard_panel_style = "default"
    listboard_model_manager_name = "objects"
    listboard_panel_title = "Subject Review"
    listboard_view_permission_codename = "edc_review_dashboard.view_subject_review_listboard"

    model_wrapper_cls = RelatedVisitModelWrapper
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

    appointment_model = "edc_appointment.appointment"

    #  attr to call SubjectReviewListboardView.urls in urls.py
    urlconfig_getattr = "review_listboard_urls"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = {}
        context.update(KEYED=KEYED, REQUIRED=REQUIRED)
        context.update(q=self.subject_identifier or self.search_term)
        return super().get_context_data(**kwargs)

    @property
    def subject_identifier(self):
        if not self._subject_identifier:
            self._subject_identifier = self.kwargs.get("subject_identifier")
            if self.appointment:
                self._subject_identifier = self.appointment.subject_identifier
        return self._subject_identifier

    @property
    def raw_search_term(self):
        return self.subject_identifier or self.request.GET.get("q")

    @property
    def appointments_wrapped(self):
        return None

    @property
    def appointment_wrapped(self):
        return None

    def get_listboard_model_manager_name(self) -> str:
        if sites.user_may_view_other_sites(self.request):
            return "objects"
        return self.listboard_model_manager_name

    def get_queryset_filter_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        q_object, options = super().get_queryset_filter_options(request, *args, **kwargs)
        if self.search_term and re.match("^[A-Z]+$", self.search_term):
            q_object |= Q(first_name__exact=self.search_term)
        if kwargs.get("subject_identifier"):
            options.update({"subject_identifier": kwargs.get("subject_identifier")})
        return q_object, options

    def get_wrapped_queryset(self, queryset):
        """Returns a list of wrapped model instances.

        Usually is passed the queryset `object_list` and wraps each
        instance just before passing to the template.
        """

        if not self.subject_identifier:
            qs = (
                queryset.order_by("subject_identifier")
                .values("subject_identifier")
                .annotate(visit_count=Count("subject_identifier"))
            )
            wrapped_results = [Row(**values) for values in qs]
        else:
            wrapped_results = []
            for obj in queryset:
                model_wrapper = self.model_wrapper_cls(obj)
                model_wrapper = self.update_wrapped_instance(model_wrapper)
                wrapped_results.append(model_wrapper)
        return wrapped_results
