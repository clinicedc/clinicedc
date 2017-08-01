from django.db import models

from .base_enrollment_model_mixin import BaseEnrollmentModelMixin


class EnrollmentModelMixin(BaseEnrollmentModelMixin, models.Model):
    """A model mixin for a schedule's enrollment model."""

    is_eligible = models.BooleanField(
        default=False,
        editable=False)

    class Meta:
        abstract = True
        visit_schedule_name = None
        unique_together = (
            'subject_identifier', 'visit_schedule_name', 'schedule_name')
