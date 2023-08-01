import re

from django.db.models import Q
from django.db.models.aggregates import Count
from edc_appointment.view_mixins import AppointmentViewMixin
from edc_dashboard.view_mixins import EdcViewMixin
from edc_listboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_listboard.views import ListboardView
from edc_metadata.constants import KEYED, REQUIRED
from edc_metadata.view_mixins import MetadataViewMixin
from edc_navbar.view_mixin import NavbarViewMixin
from edc_subject_dashboard.view_mixins import (
    RegisteredSubjectViewMixin,
    SubjectVisitViewMixin,
)
from edc_subject_model_wrappers import SubjectVisitModelWrapper
from edc_visit_schedule.view_mixins import VisitScheduleViewMixin
from edc_visit_tracking.utils import get_related_visit_model_cls


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

    model_wrapper_cls = SubjectVisitModelWrapper
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(KEYED=KEYED, REQUIRED=REQUIRED)
        context.update(q=self.search_term or "")
        return context

    @property
    def raw_search_term(self):
        if self.appointment:
            self.subject_identifier = self.appointment.subject_identifier
        return self.request.GET.get("q") or self.subject_identifier

    @property
    def appointments_wrapped(self):
        return None

    @property
    def appointment_wrapped(self):
        return None

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.search_term:
            return (
                qs.values("subject_identifier")
                .annotate(visit_count=Count("subject_identifier"))
                .order_by("-subject_identifier")
            )
        return qs

    def get_wrapped_queryset(self, queryset):
        """Returns a list of wrapped model instances.

        Usually is passed the queryset `object_list` and wraps each
        instance just before passing to the template.
        """

        class Obj:
            def __init__(self, subject_identifier, visit_count):
                self.subject_identifier = subject_identifier
                self.visit_count = visit_count

        if not self.search_term:
            wrapped_objs = [Obj(**obj) for obj in queryset]
        else:
            wrapped_objs = []
            for obj in queryset:
                model_wrapper = self.model_wrapper_cls(obj)
                model_wrapper = self.update_wrapped_instance(model_wrapper)
                wrapped_objs.append(model_wrapper)
        return wrapped_objs

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        if kwargs.get("subject_identifier"):
            options.update({"subject_identifier": kwargs.get("subject_identifier")})
        return options

    def extra_search_options(self, search_term):
        q = Q()
        if re.match("^[A-Z]+$", search_term):
            q = Q(first_name__exact=search_term)
        return q
