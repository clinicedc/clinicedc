from django.apps import apps as django_apps
from edc_constants.constants import YES, NO


class DashboardViewMixin:

    def get_template_names(self):
        return [django_apps.get_app_config(
            self.app_config_name).dashboard_template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(YES=YES, NO=NO)
        return context
