from django.db import models

from edc_content_type_map.models import ContentTypeMap


class MembershipFormManager(models.Manager):

    def get_by_natural_key(self, app_label, model):
        content_type_map = ContentTypeMap.objects.get_by_natural_key(app_label, model)
        return self.get(content_type_map=content_type_map)

    def codes_for_category(self, membership_form_category):
        """ Lists visit codes for this membership form category."""
        VisitDefinition = models.get_model('edc_visit_schedule', 'visitdefinition')
        membership_forms = super(MembershipFormManager, self).filter(category=membership_form_category)
        visit_definition_codes = set()
        for membership_form in membership_forms:
            for visit_definition in VisitDefinition.objects.filter(
                    schedule__membership_form=membership_form):
                visit_definition_codes.add(visit_definition.code)
        return list(visit_definition_codes)
