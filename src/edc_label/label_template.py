import os

from django.apps import apps as django_apps
from string import Template


class LabelTemplateError(Exception):
    pass


class LabelTemplate:

    template_name = None

    def __init__(self, template_name=None):
        app_config = django_apps.get_app_config('edc_label')
        self.template_name = template_name or self.template_name
        try:
            path = app_config.label_templates.get(template_name)
        except TypeError:
            raise LabelTemplateError(
                f'Invalid path to label template. Looking for  \'{template_name}\'. '
                f'Got {self}.')
        if not os.path.exists(path):
            raise LabelTemplateError(
                f'Invalid label template path. '
                f'Got {self}.')
        with open(path, 'r') as f:
            self.template = f.read()

    def __str__(self):
        return f'{self.template_folder}/{self.template_name}.'

    def render(self, context):
        return Template(self.template).safe_substitute(context)
