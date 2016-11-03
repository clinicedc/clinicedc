import sys

from django.apps import apps as django_apps
from django.apps import AppConfig as DjangoAppConfig

from edc_lab.site_lab_profiles import site_lab_profiles


class AppConfig(DjangoAppConfig):
    name = 'edc_lab'
    verbose_name = 'Edc Lab'
    app_label = 'edc_example'

    requisition = 'edc_example.subjectrequisition'

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_lab_profiles.autodiscover()
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    @property
    def aliquot_model(self):
        return django_apps.get_model(self.app_label, 'aliquot')

    @property
    def requisition_model(self):
        return django_apps.get_model(self.requisition)

    @property
    def specimen_collection_model(self):
        return django_apps.get_model(self.app_label, 'specimencollection')

    @property
    def specimen_collection_item_model(self):
        return django_apps.get_model(self.app_label, 'specimencollectionitem')
