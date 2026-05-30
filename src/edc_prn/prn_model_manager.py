from django.db import models


class PrnModelManager(models.Manager):
    """A manager class for PRN models"""

    use_in_migrations = True

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)
