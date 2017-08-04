import os

from string import Template
from django.apps import apps as django_apps


app_config = django_apps.get_app_config('edc_label')


class LabelTemplateError(Exception):
    pass


class LabelTemplate:

    template_name = None
    template_folder = app_config.template_folder
    label_templates = app_config.label_templates

    def __init__(self, template_name=None):
        self.template_name = template_name or self.template_name
        try:
            path = os.path.join(
                self.template_folder,
                self.label_templates.get(template_name))
        except TypeError:
            raise LabelTemplateError(
                f'Invalid template name or path. Got {template_name}')
        with open(path, 'r') as f:
            self.template = f.read()

    def __str__(self):
        return self.template_name

    def render(self, context):
        return Template(self.template).safe_substitute(context)
