import os

from django.conf import settings
from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_label'
    verbose_name = 'Edc Label'
    default_cups_server_ip = None
    default_printer_label = None
    default_template_file = os.path.join(settings.STATIC_ROOT, 'edc_label', 'label_templates', 'default.txt')
    default_label_identifier_name = 'barcode_value'
    default_template_folder = os.path.join(settings.STATIC_ROOT, 'edc_label', 'label_templates')
    extra_templates_folder = None
    default_ext = 'lbl'
    label_templates = {}

    def ready(self):
        from .label_template import LabelTemplate
        filenames = [os.path.join(self.default_template_folder, f) for f in os.listdir(self.default_template_folder)
                     if os.path.splitext(f)[1] == '.{}'.format(self.default_ext)]
        if self.extra_templates_folder:
            extra_files = [os.path.join(self.extra_templates_folder, f) for f in os.listdir(self.extra_templates_folder)
                           if os.path.splitext(f)[1] == '.{}'.format(self.default_ext)]
            filenames.extend(extra_files)
        filenames = {' '.join(os.path.splitext(f)[0].split('/')[-1:][0].split('_')): f
                     for f in filenames}
        for label, filename in filenames.items():
            label_template = LabelTemplate(label, label_template_file=filename)
            self.label_templates.update({label_template.label: label_template})
