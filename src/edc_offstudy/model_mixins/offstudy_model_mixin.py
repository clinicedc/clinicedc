from django.apps import apps as django_apps
from django.db import models
from django.db.models import options
from django.utils import timezone
from edc_base.model_fields import OtherCharField
from edc_base.model_validators import datetime_not_future
from edc_constants.date_constants import EDC_DATETIME_FORMAT
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_protocol.validators import datetime_not_before_study_start
from edc_visit_schedule.model_mixins import VisitScheduleMethodsModelMixin

from .validate_offstudy_model_mixin import ValidateOffstudyModelMixin

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('consent_model', )


class OffstudyError(Exception):
    pass


class OffstudyModelManager(models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class OffstudyModelMixin(ValidateOffstudyModelMixin, UniqueSubjectIdentifierFieldMixin,
                         VisitScheduleMethodsModelMixin, models.Model):
    """Mixin for the Off Study model.
    """

    offstudy_datetime = models.DateTimeField(
        verbose_name="Off-study Date",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future])

    reason = models.CharField(
        verbose_name="Please code the primary reason participant taken off-study",
        max_length=115)

    reason_other = OtherCharField()

    comment = models.TextField(
        max_length=250,
        verbose_name="Comment",
        blank=True,
        null=True)

    objects = OffstudyModelManager()

    def save(self, *args, **kwargs):
        if not self.consented_before_offstudy:
            formatted_date = timezone.localtime(
                self.offstudy_datetime).strftime(EDC_DATETIME_FORMAT)
            raise OffstudyError(
                f'Offstudy date may not be before the date of consent. '
                f'Got {formatted_date}.')
        app_config = django_apps.get_app_config('edc_visit_tracking')
        visit_model_cls = app_config.visit_model_cls(self._meta.app_label)
        app_config = django_apps.get_app_config('edc_appointment')
        appointment_model_cls = django_apps.get_model(app_config.get_configuration(
            related_visit_model=visit_model_cls._meta.label_lower).model)
        self.offstudy_datetime_after_last_visit_or_raise(
            visit_model_cls=visit_model_cls)
        appointment_model_cls.objects.delete_for_subject_after_date(
            self.subject_identifier, self.offstudy_datetime)
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier, )

    def __str__(self):
        formatted_date = timezone.localtime(
            self.offstudy_datetime).strftime(EDC_DATETIME_FORMAT)
        return f'{self.subject_identifier} {formatted_date}'

    class Meta:
        abstract = True
        consent_model = None
