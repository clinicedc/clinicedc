import os

from string import Template

from django.apps import apps as django_apps


class LabelTemplate:

    def __init__(self, template_name=None):
        app_config = django_apps.get_app_config('edc_label')
        self.template_name = template_name
        self.filename = os.path.join(
            app_config.template_folder,
            template_name + '.' + app_config.template_ext)
        with open(self.filename, 'r') as f:
            self.template = f.read()

    def __str__(self):
        return self.template_name

    def render(self, context):
        return Template(self.template).safe_substitute(context)
