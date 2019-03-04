from edc_base.view_mixins import EdcBaseViewMixin

from .action_view import ActionView


class BoxView(EdcBaseViewMixin, ActionView):
    def form_actions(self):
        pass
