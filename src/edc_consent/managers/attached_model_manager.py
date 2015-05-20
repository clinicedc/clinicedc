from django.db import models


class AttachedModelManager(models.Manager):

    def get_by_natural_key(self, name, version, app_label, model):
        ContentTypeMap = models.get_model('bhp_content_type_map', 'ContentTypeMap')
        content_type_map = ContentTypeMap.objects.get_by_natural_key(app_label, model)
        ConsentCatalogue = models.get_model('edc_consent', 'ConsentCatalogue')
        consent_catalogue = ConsentCatalogue.objects.get_by_natural_key(name, version)
        #AttachedModel = models.get_model('edc_consent', 'AttachedModel')
        return self.get(content_type_map=content_type_map, consent_catalogue=consent_catalogue)
        #return AttachedModel.objects.get(content_type_map=content_type_map, consent_catalogue=consent_catalogue)
