from django.db import models


class RegisteredSubjectManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, subject_identifier_as_pk):
        return self.get(subject_identifier_as_pk=subject_identifier_as_pk)

    def get_for_subject_identifier(self, subject_identifier):
        """Returns a queryset for the given subject_identifier."""
        options = {"subject_identifier": subject_identifier}
        return self.filter(**options)

    def get_for_visit(self, visit):
        options = {"subject_identifier": visit.subject_identifier}
        return self.get(**options)
