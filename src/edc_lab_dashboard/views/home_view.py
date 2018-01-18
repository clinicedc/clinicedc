from django.views.generic.base import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from ..dashboard_templates import dashboard_templates


class HomeView(EdcBaseViewMixin, NavbarViewMixin, TemplateView):

    template_name = dashboard_templates.get('home_template')
    navbar_name = 'specimens'
    navbar_selected_item = 'specimens'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context.update(
#             receive_listboard_url_name=self.app_config.receive_listboard_url_name,
#             process_listboard_url_name=self.app_config.process_listboard_url_name,
#             pack_listboard_url_name=self.app_config.pack_listboard_url_name,
#             manifest_listboard_url_name=self.app_config.manifest_listboard_url_name,
#             base_template_name=self.base_template_name
#         )
#         return context
