from edc_base.view_mixins import EdcBaseViewMixin

from .action_view import ActionView


class BoxView(EdcBaseViewMixin, ActionView):

    template_name = 'edc_lab_dashboard/home.html'
    navbar_name = 'specimens'

    def form_actions(self):
        pass
