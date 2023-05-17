from edc_dashboard.view_mixins import EdcViewMixin
from edc_listboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_listboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ...view_mixins import FormActionViewMixin


class BaseListboardView(
    EdcViewMixin,
    FormActionViewMixin,
    SearchFormViewMixin,
    NavbarViewMixin,
    ListboardFilterViewMixin,
    ListboardView,
):
    navbar_name = "specimens"
