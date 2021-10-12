import os
from string import Template

from django.apps import apps as django_apps
from django.contrib.staticfiles import finders


class LabelTemplateError(Exception):
    pass


class LabelTemplate:

    template_name = None

    def __init__(self, template_name=None, static_files_path=None):
        if static_files_path:
            path = finders.find(os.path.join(static_files_path, template_name))
        else:
            app_config = django_apps.get_app_config("edc_label")
            self.template_name = template_name or self.template_name
            try:
                path = app_config.label_templates[template_name]
            except KeyError:
                raise LabelTemplateError(
                    f"Invalid label template name. "
                    f"Expected one of {list(app_config.label_templates.keys())}. "
                    f"Got '{template_name}'. "
                    f"See edc_label.app_config."
                )
        if not os.path.exists(path or ""):
            raise LabelTemplateError(
                f"Invalid label template path. "
                f"Looking for  template '{template_name}'. "
                f"Got {path}. See edc_label.app_config."
            )
        with open(path, "r") as f:
            self.template = f.read()

    def __str__(self):
        return self.template_name

    def render(self, context):
        return Template(self.template).safe_substitute(context)
