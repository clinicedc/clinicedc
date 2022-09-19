from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_model.validators import datetime_not_future
from edc_model_fields.fields import OtherCharField
from edc_protocol.validators import datetime_not_before_study_start
from edc_utils import formatted_datetime, get_utcnow
from edc_visit_schedule.utils import (
    off_all_schedules_or_raise,
    offstudy_datetime_after_all_offschedule_datetimes,
)

from ..choices import OFFSTUDY_REASONS
from ..utils import OffstudyError


class OffstudyModelMixinError(ValidationError):
    pass


class OffstudyModelManager(models.Manager):
    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class OffstudyModelMixin(UniqueSubjectIdentifierFieldMixin, models.Model):
    """Model mixin for the Off-study model.

    Override in admin like this:

        def formfield_for_choice_field(self, db_field, request, **kwargs):
            if db_field.name == "offstudy_reason":
                kwargs['choices'] = OFFSTUDY_REASONS
            return super().formfield_for_choice_field(db_field, request, **kwargs)

    """

    offstudy_reason_choices = OFFSTUDY_REASONS

    offstudy_datetime = models.DateTimeField(
        verbose_name="Off-study date and time",
        validators=[datetime_not_before_study_start, datetime_not_future],
        default=get_utcnow,
    )

    offstudy_reason = models.CharField(
        verbose_name="Please code the primary reason participant taken off-study",
        choices=offstudy_reason_choices,
        max_length=125,
    )

    other_offstudy_reason = OtherCharField()

    comment = models.TextField(
        verbose_name="Please provide further details if possible",
        max_length=500,
        blank=True,
        null=True,
    )

    def __str__(self):
        local = timezone.localtime(self.offstudy_datetime)
        return f"{self.subject_identifier} {formatted_datetime(local)}"

    def save(self, *args, **kwargs):
        off_all_schedules_or_raise(subject_identifier=self.subject_identifier)
        offstudy_datetime_after_all_offschedule_datetimes(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=self.offstudy_datetime,
            exception_cls=OffstudyError,
        )
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier,)

    @property
    def report_datetime(self):
        return self.offstudy_datetime

    class Meta:
        abstract = True
