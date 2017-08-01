from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .base_action_view import BaseActionView


app_config = django_apps.get_app_config('edc_lab_dashboard')


class BoxView(BaseActionView):

    template_name = 'edc_lab_dashboard/home.html'
    navbar_name = 'specimens'
    listboard_url_name = app_config.pack_listboard_url_name

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_actions(self):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
