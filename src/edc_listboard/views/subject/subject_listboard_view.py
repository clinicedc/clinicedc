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

    name_search_field: str = "first_name"
    identity_regex: str = r"^[0-9]+$"
    identity_fields = ["identity"]

    def get_queryset_filter_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        q_object, options = super().get_queryset_filter_options(request, *args, **kwargs)
        if kwargs.get("subject_identifier"):
            options.update({"subject_identifier": kwargs.get("subject_identifier")})
        if self.search_term:
            q_object |= Q(user_created__iexact=self.search_term)
            q_object |= Q(user_modified__iexact=self.search_term)
            if re.match(r"^[A-Za-z\-\s]+$", self.search_term):
                q_object |= Q(initials__exact=self.search_term.upper())
                q_object |= Q(**{f"{self.name_search_field}__exact": self.search_term.upper()})
                q_object |= Q(
                    screening_identifier__icontains=self.search_term.replace("-", "").upper()
                )
                q_object |= Q(subject_identifier__icontains=self.search_term)
            if re.match(self.identity_regex, self.search_term or ""):
                for field in self.identity_fields:
                    q_object |= Q(**{f"{field}__exact": self.search_term})
        return q_object, options
