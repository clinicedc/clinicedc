from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .base_action_view import BaseActionView


class BoxView(BaseActionView):

    template_name = 'edc_lab_dashboard/home.html'
    navbar_name = 'specimens'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_actions(self):
        pass
