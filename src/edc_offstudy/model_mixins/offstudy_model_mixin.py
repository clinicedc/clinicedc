from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from edc_base.model_validators import datetime_not_future
from edc_base.utils import get_utcnow
from edc_constants.date_constants import EDC_DATETIME_FORMAT
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_model_fields.fields import OtherCharField
from edc_protocol.validators import datetime_not_before_study_start

from ..choices import OFF_STUDY_REASONS
from ..offstudy import Offstudy

# if 'consent_model' not in options.DEFAULT_NAMES:
#     options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('consent_model',)
#
# MISSING_META_CONSENT_MODEL = 'missing_meta_consent_model'
# LOOKUP_ERROR = 'lookup_error'


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

    offstudy_cls = Offstudy
    offstudy_reason_choices = OFF_STUDY_REASONS

    offstudy_datetime = models.DateTimeField(
        verbose_name="Off-study date and time",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        default=get_utcnow)

    offstudy_reason = models.CharField(
        verbose_name="Please code the primary reason participant taken off-study",
        choices=offstudy_reason_choices,
        max_length=125)

    offstudy_reason_other = OtherCharField()

    objects = OffstudyModelManager()

    def save(self, *args, **kwargs):
        self.offstudy_cls(
            offstudy_model=self._meta.label_lower,
            **self.__dict__)
        super().save(*args, **kwargs)

    @property
    def report_datetime(self):
        return self.offstudy_datetime

    def natural_key(self):
        return (self.subject_identifier, )

    def __str__(self):
        formatted_date = timezone.localtime(
            self.offstudy_datetime).strftime(EDC_DATETIME_FORMAT)
        return f'{self.subject_identifier} {formatted_date}'

    class Meta:
        abstract = True
