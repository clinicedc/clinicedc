from django.apps import apps
from django.db import models

from edc_content_type_map.models import ContentTypeMap


class MemberManager(models.Manager):

    def get_by_natural_key(self, app_label, model):
        """Returns the natural key for serialization."""
        content_type_map = ContentTypeMap.objects.get_by_natural_key(app_label, model)
        return self.get(content_type_map=content_type_map)

    def codes_for_category(self, member_category):
        """ Lists visit codes for this membership category."""
        VisitDefinition = apps.get_model('edc_visit_schedule', 'visitdefinition')
        members = super(MemberManager, self).filter(category=member_category)
        visit_definition_codes = set()
        for member in members:
            for visit_definition in VisitDefinition.objects.filter(schedule_group__member=member):
                visit_definition_codes.add(visit_definition.code)
        return list(visit_definition_codes)
