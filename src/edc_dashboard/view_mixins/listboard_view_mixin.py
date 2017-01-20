from django.apps import apps as django_apps


class ListboardViewMixin:

    def get_template_names(self):
        return [django_apps.get_app_config(self.app_config_name).listboard_template_name]
