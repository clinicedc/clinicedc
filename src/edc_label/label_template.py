import json

from string import Template

from django.apps import apps as django_apps

app_config = django_apps.get_app_config('edc_label')


class LabelTemplate:

    def __init__(self, label, label_template_file, verbose_name=None, ):
        self.label = label
        self.verbose_name = verbose_name or ' '.join([x.capitalize() for x in self.label.split('_')]) + ' Label'
        self.file = label_template_file.split('/')[-1:][0]
        self.filename = label_template_file or app_config.default_template_file
        with open(self.filename, 'r') as f:
            self.label_template = f.read()

    def __str__(self):
        return self.verbose_name

    def render(self, context):
        return Template(self.label_template).safe_substitute(context)

    def to_json(self):
        return json.dumps(self.__dict__)
