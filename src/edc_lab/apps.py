import sys

from django.apps import apps as django_apps
from django.apps import AppConfig as DjangoAppConfig

from edc_lab.site_labs import site_labs


class AppConfig(DjangoAppConfig):
    name = 'edc_lab'
    verbose_name = 'Edc Lab'
    lab_models = {
        'aliquot': 'edc_lab.aliquot',
        'specimencollection': 'edc_lab.specimencollection',
        'specimencollectionitem': 'edc_lab.specimencollectionitem',
    }

    def ready(self):
        sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
        site_labs.autodiscover()
        sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))

    def model(self, model_name):
        return django_apps.get_model(
            *self.lab_models.get(model_name).split('.'))

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
