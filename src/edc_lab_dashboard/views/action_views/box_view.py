from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .action_view import ActionView


class BoxView(ActionView):

    template_name = 'edc_lab_dashboard/home.html'
    navbar_name = 'specimens'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_actions(self):
        pass
