from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin


app_config = django_apps.get_app_config('edc_lab_dashboard')


class HomeView(EdcBaseViewMixin, AppConfigViewMixin, TemplateView):

    template_name = 'edc_lab_dashboard/home.html'
    navbar_name = 'specimens'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            receive_listboard_url_name=app_config.receive_listboard_url_name,
            process_listboard_url_name=app_config.process_listboard_url_name,
            pack_listboard_url_name=app_config.pack_listboard_url_name,
            manifest_listboard_url_name=app_config.manifest_listboard_url_name,
            base_template_name=app_config.base_template_name
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
