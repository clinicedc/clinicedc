from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import options
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin

from .base_enrollment_model_mixin import BaseEnrollmentModelMixin

if 'visit_schedule_name' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('visit_schedule_name',)

if 'consent_model' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('consent_model',)


class EnrollmentModelMixin(UniqueSubjectIdentifierFieldMixin,
                           BaseEnrollmentModelMixin, models.Model):
    """A model mixin for a schedule's enrollment model.
    """

    consent_identifier = models.UUIDField()

    is_eligible = models.BooleanField(
        default=False,
        editable=False)

    def save(self, *args, **kwargs):
        if not self._meta.consent_model:
            raise ImproperlyConfigured(
                'Consent model attribute not set. Got '
                f'\'{self._meta.label_lower}.consent_model\' = None')
        elif not self._meta.visit_schedule_name:
            raise ImproperlyConfigured(
                'Visit schedule name attribute not set. Got '
                f'\'{self._meta.label_lower}.visit_schedule_name\' = None')
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        visit_schedule_name = None
        consent_model = None
        unique_together = (
            'subject_identifier', 'visit_schedule_name', 'schedule_name')
