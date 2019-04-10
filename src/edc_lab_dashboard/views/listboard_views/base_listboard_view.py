from edc_dashboard.view_mixins import (
    EdcViewMixin,
    ListboardFilterViewMixin,
    SearchFormViewMixin,
)
from edc_dashboard.views import ListboardView
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
