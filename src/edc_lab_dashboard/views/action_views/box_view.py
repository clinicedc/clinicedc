from edc_dashboard.view_mixins import EdcViewMixin

from .action_view import ActionView


class BoxView(EdcViewMixin, ActionView):
    def form_actions(self):
        pass
