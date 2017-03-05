import os

from string import Template

from django.apps import apps as django_apps


app_config = django_apps.get_app_config('edc_label')


class LabelTemplate:

    template_name = None
    template_folder = app_config.template_folder
    template_ext = app_config.template_ext

    def __init__(self, template_name=None):
        if template_name:
            self.template_name = template_name
        filename = os.path.join(
            self.template_folder, template_name + '.' + self.template_ext)
        with open(filename, 'r') as f:
            self.template = f.read()

    def __str__(self):
        return self.template_name

    def render(self, context):
        return Template(self.template).safe_substitute(context)
