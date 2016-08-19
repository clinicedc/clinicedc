import os

from django.conf import settings
from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_label'
    verbose_name = 'Edc Label'
    # IP address of the CUPS server, if localhost leave as None
    default_cups_server_ip = None
    # CUPS name of the default printer
    default_printer_label = None
    # the default template file to use if not specifiedwhen printing
    default_template_file = os.path.join(settings.STATIC_ROOT, 'edc_label', 'label_templates', 'default.txt')
    # full path to edc_label static templates folder, do not change
    default_template_folder = os.path.join(settings.STATIC_ROOT, 'edc_label', 'label_templates')
    # path to additional template files, if any
    extra_templates_folder = None
    # default extension, do not change
    default_ext = 'lbl'
    # a template variable name that has a unique value
    default_label_identifier_name = 'barcode_value'
    # updated below
    label_templates = {}

    def ready(self):
        self.update_label_templates()

    def update_label_templates(self):
        """Read in label template files from both default and extra folder."""
        from .label_template import LabelTemplate
        filenames = [os.path.join(self.default_template_folder, f) for f in os.listdir(self.default_template_folder)
                     if os.path.splitext(f)[1] == '.{}'.format(self.default_ext)]
        if self.extra_templates_folder:
            extra_files = [os.path.join(self.extra_templates_folder, f) for f in os.listdir(self.extra_templates_folder)
                           if os.path.splitext(f)[1] == '.{}'.format(self.default_ext)]
            filenames.extend(extra_files)
        filenames = {os.path.splitext(f)[0].split('/')[-1:][0]: f
                     for f in filenames}
        for label, filename in filenames.items():
            label_template = LabelTemplate(label, label_template_file=filename)
            self.label_templates.update({label_template.label: label_template})
