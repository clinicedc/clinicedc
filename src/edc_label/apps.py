import json
import os
import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings

from edc_label.constants import LABELS, TESTDATA
from django.core.management.color import color_style

style = color_style()


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
    default_testdata_ext = 'json'
    # a template variable name that has a unique value
    default_label_identifier_name = 'barcode_value'
    # updated below
    label_templates = {}

    def ready(self):
        self.update_label_templates()

    def update_label_templates(self):
        """Read in label template files and test data from both default and extra folder.

        test data files contain a json object and use the same name as label file but
        with the .json extension."""
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        from .label_template import LabelTemplate
        filenames = {'labels': {}, 'test_data': {}}
        for section, ext in [('labels', self.default_ext), ('test_data', self.default_testdata_ext)]:
            for folder in [self.default_template_folder, self.extra_templates_folder]:
                if folder:
                    sys.stdout.write(' * looking for {} in {} ...\r'.format(section, folder))
                    try:
                        filenames[section] = [os.path.join(folder, f)
                                              for f in os.listdir(folder)
                                              if os.path.splitext(f)[1] == '.{}'.format(ext)]
                        sys.stdout.write(' * looking for {} in {} ... found.\n'.format(section, folder))
                    except FileNotFoundError:
                        sys.stdout.write(' * looking for {} in {} ... '.format(section, folder) + style.ERROR('error') + '.\n')
            filenames[section] = {os.path.splitext(f)[0].split('/')[-1:][0]: f
                                  for f in filenames[section]}

        for label, filename in filenames[LABELS].items():
            label_template = LabelTemplate(label, label_template_file=filename)
            try:
                with open(filenames[TESTDATA].get(label, None), 'r') as f:
                    label_template.test_context = json.loads(f.read())[label]
            except TypeError:
                label_template.test_context = {}
            self.label_templates.update({label_template.label: label_template})
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
