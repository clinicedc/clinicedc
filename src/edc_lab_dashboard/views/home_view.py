from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_navbar import NavbarViewMixin


class HomeView(EdcBaseViewMixin, NavbarViewMixin, AppConfigViewMixin, TemplateView):

    template_name = 'edc_lab_dashboard/home.html'
    navbar_name = 'specimens'
    navbar_selected_item = 'specimens'
    app_config_name = 'edc_lab_dashboard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            receive_listboard_url_name=self.app_config.receive_listboard_url_name,
            process_listboard_url_name=self.app_config.process_listboard_url_name,
            pack_listboard_url_name=self.app_config.pack_listboard_url_name,
            manifest_listboard_url_name=self.app_config.manifest_listboard_url_name,
            base_template_name=self.base_template_name
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
