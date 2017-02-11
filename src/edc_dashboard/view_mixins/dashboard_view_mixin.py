from django.apps import apps as django_apps


class DashboardViewMixin:

    def get_template_names(self):
        return [django_apps.get_app_config(
            self.app_config_name).dashboard_template_name]
