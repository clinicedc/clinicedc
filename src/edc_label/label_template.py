from pathlib import Path
from string import Template

from django.apps import apps as django_apps
from django.contrib.staticfiles import finders
from django.core.exceptions import ObjectDoesNotExist


class LabelTemplateError(Exception):
    pass


class LabelTemplate:
    template_name = None

    def __init__(self, template_name=None, static_files_path=None):
        self.template_name = template_name or self.template_name
        try:
            zpl_label_template = django_apps.get_model(
                "edc_label.zpllabeltemplates"
            ).objects.get(name=self.template_name)
        except ObjectDoesNotExist as e:
            if static_files_path:
                path = finders.find(str(Path(static_files_path) / template_name))
            else:
                app_config = django_apps.get_app_config("edc_label")
                try:
                    path = app_config.label_templates[template_name]
                except KeyError as e:
                    raise LabelTemplateError(
                        f"Invalid label template name. "
                        f"Expected one of {list(app_config.label_templates.keys())}. "
                        f"Got '{template_name}'. "
                        f"See edc_label.app_config."
                    ) from e
            if not path or not Path(path).exists():
                raise LabelTemplateError(
                    f"Invalid label template path. "
                    f"Looking for  template '{template_name}'. "
                    f"Got {path}. See edc_label.app_config."
                ) from e
            with Path(path).open("r") as f:
                self.template = f.read()
        else:
            self.template = zpl_label_template.zpl_data.strip()

    def __str__(self):
        return self.template_name

    def render(self, context):
        zpl_string = Template(self.template).safe_substitute(context)
        return zpl_string.replace("\n", "").replace("\r", "")
