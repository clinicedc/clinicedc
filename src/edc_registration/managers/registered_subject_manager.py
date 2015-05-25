from django.apps import apps

from ..managers import BaseSubjectManager


class RegisteredSubjectManager(BaseSubjectManager):

    def get_by_natural_key(self, subject_identifier_as_pk):
        RegisteredSubject = apps.get_model('registration', 'RegisteredSubject')
        registered_subject = RegisteredSubject.objects.get_by_natural_key(subject_identifier_as_pk)
        return self.get(registered_subject=registered_subject)
