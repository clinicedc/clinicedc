from django.db import models


class SubjectIdentifierManager(models.Manager):

    use_in_migrations = True

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class IdentifierManager(models.Manager):
    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)
