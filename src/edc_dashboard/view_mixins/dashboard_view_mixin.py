from django.apps import apps as django_apps


class DashboardViewMixin:

    navbar_selected = None

    def get_navbar_selected(self):
        return self.navbar_selected or self.app_config_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            navbar_selected=self.get_navbar_selected())
        return context

    def get_template_names(self):
        return [django_apps.get_app_config(self.app_config_name).dashboard_template_name]
