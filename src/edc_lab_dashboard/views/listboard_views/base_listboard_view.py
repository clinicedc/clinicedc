from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ...view_mixins import FormActionViewMixin, ModelsViewMixin


class BaseListboardView(FormActionViewMixin, SearchFormViewMixin, ModelsViewMixin, NavbarViewMixin,
                        ListboardFilterViewMixin, EdcBaseViewMixin, ListboardView):

    action_name = None
    form_action_name = 'form_action'
    form_action_selected_items_name = 'selected_items'
    form_action_url = None
    navbar_name = 'specimens'
    search_form_url = None
