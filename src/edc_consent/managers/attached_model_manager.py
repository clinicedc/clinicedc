from django.apps import apps
from django.db import models


class AttachedModelManager(models.Manager):

    def get_by_natural_key(self, name, version, app_label, model):
        ContentTypeMap = apps.get_model('bhp_content_type_map', 'ContentTypeMap')
        content_type_map = ContentTypeMap.objects.get_by_natural_key(app_label, model)
        ConsentCatalogue = apps.get_model('edc_consent', 'ConsentCatalogue')
        consent_catalogue = ConsentCatalogue.objects.get_by_natural_key(name, version)
        return self.get(content_type_map=content_type_map, consent_catalogue=consent_catalogue)
