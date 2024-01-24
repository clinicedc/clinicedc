from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ...view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from ..listboard_view import ListboardView


class SubjectListboardView(
    EdcViewMixin,
    NavbarViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
    ListboardView,
):
    listboard_model = None

    listboard_template: str = "subject_listboard_template"
    listboard_url: str = "subject_listboard_url"
    listboard_panel_style: str = "success"
    listboard_fa_icon: str = "fas fa-user-circle fa-2x"
    listboard_view_permission_codename: str = "edc_subject_dashboard.view_subject_listboard"

    navbar_selected_item: str = "consented_subject"
    search_form_url: str = "subject_listboard_url"

    search_fields: list[str] = [
        "user_created",
        "user_modified",
        "screening_identifier",
        "subject_identifier",
        "initials__exact",
        "identity__exact",
        "first_name__exact",
    ]

    def get_listboard_model(self) -> str:
        return self.listboard_model
