import re

from django.db.models import Q
from edc_consent.utils import get_consent_model_name
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_subject_model_wrappers import SubjectConsentModelWrapper

from ...view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from ..listboard_view import ListboardView


class SubjectListboardView(
    EdcViewMixin,
    NavbarViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    ListboardView,
):

    listboard_model = get_consent_model_name()
    model_wrapper_cls = SubjectConsentModelWrapper

    listboard_template = "subject_listboard_template"
    listboard_url = "subject_listboard_url"
    listboard_panel_style = "success"
    listboard_fa_icon = "fas fa-user-circle fa-2x"
    listboard_view_permission_codename = "edc_subject_dashboard.view_subject_listboard"

    navbar_selected_item = "consented_subject"
    search_form_url = "subject_listboard_url"

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        if kwargs.get("subject_identifier"):
            options.update({"subject_identifier": kwargs.get("subject_identifier")})
        return options

    def extra_search_options(self, search_term):
        q_objects = [
            Q(user_created__iexact=search_term),
            Q(user_modified__iexact=search_term),
        ]
        if re.match(r"^[A-Za-z\-]+$", search_term):
            q_objects.append(Q(initials__exact=search_term.upper()))
            q_objects.append(Q(first_name__exact=search_term.upper()))
            q_objects.append(
                Q(screening_identifier__icontains=search_term.replace("-", "").upper())
            )
            q_objects.append(Q(subject_identifier__icontains=search_term))
        if re.match(r"^[0-9]+$", search_term):
            q_objects.append(Q(identity__exact=search_term))
        return q_objects
