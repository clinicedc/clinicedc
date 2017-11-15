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
            subject_type_obj = site_protocol_subjects.get(
                name=self.get_enrollment_subject_type(),
                model=self._meta.label_lower)
            if not subject_type_obj:
                key = site_protocol_subjects._key(
                    name=self.get_enrollment_subject_type(),
                    model=self._meta.label_lower)
                raise InvalidSubjectType(
                    f'Invalid subject type. Got \'{key}\'. See site_protocol_subjects.')
            self.cap_count, self.cap = subject_type_obj.fetch_count_or_raise(
                study_site=self.get_enrollment_study_site())
        super().save(*args, **kwargs)

    def get_enrollment_study_site(self):
        try:
            study_site = self.study_site
        except AttributeError:
            study_site = None  # will default to ALL_SITES
        return study_site

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
