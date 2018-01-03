from django.db import models
from django.db.models import options

from .default_subject_type import default_subject_type
from django.core.exceptions import ImproperlyConfigured
from edc_protocol.site_protocol_subjects import site_protocol_subjects

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('subject_type', )


class InvalidSubjectType(Exception):
    pass


class EnrollmentCapModelMixin(models.Model):

    """Blocks new instances once a record count is reached.
    """

    cap_count = models.IntegerField(editable=False)

    cap = models.IntegerField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            site_protocol_subjects.raise_on_max_subjects(
                model=self._meta.label_lower, **self.__dict__)
        super().save(*args, **kwargs)

    def get_enrollment_site(self):
        try:
            return self.site
        except AttributeError:
            return None  # will default to ALL_SITES
        return None

    def get_enrollment_subject_type(self):
        try:
            subject_type = self.subject_type
        except AttributeError:
            try:
                subject_type = self._meta.subject_type
            except AttributeError:
                raise ImproperlyConfigured(
                    f'Missing Meta class attr \'subject_type_name\'. See model {repr(self)}.')
        return subject_type or default_subject_type

    class Meta:
        abstract = True
        subject_type = None
