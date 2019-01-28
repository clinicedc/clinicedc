import re

from django.db.models import Q
from django.db.models.aggregates import Count
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView as BaseListboardView
from edc_navbar import NavbarViewMixin
from edc_metadata.constants import REQUIRED, KEYED

from ..model_wrappers import SubjectVisitModelWrapper


class SubjectReviewListboardView(
    NavbarViewMixin,
    EdcBaseViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    BaseListboardView,
):

    """
    Declare in your app:

        class SubjectReviewListboardView(Base):

            listboard_model = 'ambition_subject.subjectvisit'
            model_wrapper_cls = SubjectVisitModelWrapper
            navbar_name = 'ambition_dashboard'

    Add URLs:

        subject_listboard_url_config = UrlConfig(
            url_name='subject_listboard_url',
            view_class=SubjectListboardView,
            label='subject_listboard',
            identifier_label='subject_identifier',
            identifier_pattern=subject_identifier)
        urlpatterns += subject_review_listboard_url_config.listboard_urls

    """

    listboard_model = None  # e.g. 'ambition_subject.subjectvisit'
    navbar_name = None  # e.g. 'ambition_dashboard'

    listboard_template = "subject_review_listboard_template"
    listboard_url = "subject_review_listboard_url"
    listboard_panel_style = "success"
    listboard_fa_icon = "far fa-user-circle"
    listboard_model_manager_name = "objects"
    listboard_panel_title = "Subject Review"
    listboard_view_permission_codename = "edc_dashboard.view_subject_review_listboard"
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(KEYED=KEYED, REQUIRED=REQUIRED)
        if self.search_term:
            context.update(q=self.search_term)
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.search_term:
            return (
                qs.values("subject_identifier")
                .annotate(visit_count=Count("subject_identifier"))
                .order_by("subject_identifier")
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
