import os
import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.management.color import color_style

style = color_style()


class EdcLabelAppConfigError(Exception):
    pass


class AppConfig(DjangoAppConfig):
    name = "edc_label"

    verbose_name = "Edc Label"
    include_in_administration_section = True
    # default extension
    template_ext = "lbl"

    label_templates = {}

    def ready(self):
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        try:
            label_template_folder = settings.LABEL_TEMPLATE_FOLDER
        except AttributeError:
            label_template_folder = os.path.join(settings.BASE_DIR, "label_templates")
            sys.stdout.write(" Using default label template path,)\n")
            sys.stdout.write(" to customize set LABEL_TEMPLATE_FOLDER in settings.\n")
        sys.stdout.write(" Label template folder is '{label_template_folder}'.\n")
        if not os.path.exists(label_template_folder):
            sys.stdout.write(
                style.ERROR(
                    "Label template folder does not exist!\n" "Not loading label templates\n"
                )
            )
        else:
            for filename in os.listdir(label_template_folder):
                if filename.endswith(self.template_ext):
                    label_name = filename.split(".")[0]
                    self.label_templates.update(
                        {label_name: os.path.join(label_template_folder, filename)}
                    )
                    sys.stdout.write(f" * {filename}\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
