from django.apps import apps
from django.db import models


class AppointmentManager(models.Manager):
    def get_by_natural_key(self, visit_instance, visit_definition_code, subject_identifier_as_pk):
        RegisteredSubject = apps.get_model('registration', 'RegisteredSubject')
        VisitDefinition = apps.get_model('visit_schedule', 'VisitDefinition')
        registered_subject = RegisteredSubject.objects.get_by_natural_key(subject_identifier_as_pk)
        visit_definition = VisitDefinition.objects.get_by_natural_key(visit_definition_code)
        return self.get(
            registered_subject=registered_subject,
            visit_definition=visit_definition,
            visit_instance=visit_instance)
