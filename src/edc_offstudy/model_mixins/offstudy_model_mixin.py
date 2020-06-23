from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_model.models import datetime_not_future
from edc_model_fields.fields import OtherCharField
from edc_protocol.validators import datetime_not_before_study_start
from edc_utils import get_utcnow, formatted_datetime

from ..choices import OFF_STUDY_REASONS
from ..utils import off_all_schedules_or_raise


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
                kwargs['choices'] = OFF_STUDY_REASONS
            return super().formfield_for_choice_field(db_field, request, **kwargs)

    """

    offstudy_reason_choices = OFF_STUDY_REASONS

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

    offstudy_reason_other = OtherCharField()

    def __str__(self):
        local = timezone.localtime(self.offstudy_datetime)
        return f"{self.subject_identifier} {formatted_datetime(local)}"

    def save(self, *args, **kwargs):
        off_all_schedules_or_raise(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=self.offstudy_datetime,
        )
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier,)

    @property
    def report_datetime(self):
        return self.offstudy_datetime

    class Meta:
        abstract = True
