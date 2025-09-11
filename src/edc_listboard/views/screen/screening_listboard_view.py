from django.db.models import Q

from edc_constants.constants import ABNORMAL
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_screening.utils import get_subject_screening_model

from ...view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from ..listboard_view import ListboardView
from .listboard_view_filter import ScreeningListboardViewFilters


class ScreeningListboardView(
    EdcViewMixin,
    NavbarViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    ListboardView,
):
    listboard_model = get_subject_screening_model()
    listboard_view_filters = ScreeningListboardViewFilters()

    listboard_template = "screening_listboard_template"
    listboard_url = "screening_listboard_url"
    listboard_panel_style = "info"
    listboard_fa_icon = "fas fa-user-plus"
    listboard_view_permission_codename = "edc_screening.view_screening_listboard"
    alternate_search_attr = "screening_identifier"
    navbar_selected_item = "screened_subject"
    ordering = "-report_datetime"
    paginate_by = 10
    search_form_url = "screening_listboard_url"
    search_fields = [
        "screening_identifier",
        "initials__exact",
        "subject_identifier",
        "user_created",
        "user_modified",
    ]

    def get_context_data(self, **kwargs) -> dict:
        kwargs.update(
            subject_screening_add_url=self.get_subject_screening_add_url(),
            ABNORMAL=ABNORMAL,
        )
        return super().get_context_data(**kwargs)

    def get_subject_screening_add_url(self) -> str:
        return self.listboard_model_cls().get_absolute_url()

    def get_queryset_filter_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        q_object, options = super().get_queryset_filter_options(request, *args, **kwargs)
        if kwargs.get("screening_identifier"):
            options.update({"screening_identifier": kwargs.get("screening_identifier")})
        return q_object, options
