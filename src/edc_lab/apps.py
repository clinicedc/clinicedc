import sys

from django.apps import apps as django_apps
from django.apps import AppConfig as DjangoAppConfig

from edc_lab.site_lab_profiles import site_lab_profiles


class AppConfig(DjangoAppConfig):
    name = 'edc_lab'
    verbose_name = 'Edc Lab'
    custom_models = {
        'requisition': 'edc_example.subjectrequisition'}

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_lab_profiles.autodiscover()
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    def model(self, model_name):
        return django_apps.get_model(
            *self.custom_models.get(model_name, '{}.{}'.format(self.name, model_name)).split('.'))

    @property
    def aliquot_model(self):
        return self.model('aliquot')

#     @property
#     def requisition_model(self):
#         return self.model('requisition')

    @property
    def specimen_collection_model(self):
        return self.model('specimencollection')

    @property
    def specimen_collection_item_model(self):
        return self.model('specimencollectionitem')
