from django.apps import apps as django_apps
from django.db import models
from django.db.models import options
from django.utils import timezone
from edc_base.model_fields import OtherCharField
from edc_base.model_validators import datetime_not_future
from edc_base.utils import get_utcnow
from edc_constants.date_constants import EDC_DATETIME_FORMAT
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_protocol.validators import datetime_not_before_study_start
from edc_visit_schedule.model_mixins import VisitScheduleMethodsModelMixin

from ..choices import OFF_STUDY_REASONS
from ..offstudy import Offstudy
from edc_visit_schedule.model_mixins.visit_schedule_model_mixins import VisitScheduleMetaMixin

if 'consent_model' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('consent_model',)


class OffstudyModelMixinError(Exception):
    pass


class OffstudyModelManager(models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class OffstudyModelMixin(UniqueSubjectIdentifierFieldMixin,
                         VisitScheduleMethodsModelMixin, models.Model):
    """Model mixin for the Off-study model.
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
        try:
            consent_model = self._meta.consent_model
        except AttributeError as e:
            raise OffstudyModelMixinError(
                f'Missing Meta class option. See {repr(self)}. Got {e}.')
        else:
            try:
                consent_model_cls = django_apps.get_model(consent_model)
            except (AttributeError, LookupError) as e:
                raise OffstudyModelMixinError(
                    f'Invalid consent model. See Meta options '
                    f'for {repr(self)}. Got {e}.')
        self.offstudy_cls(
            consent_model_cls=consent_model_cls,
            label_lower=self._meta.label_lower,
            **self.__dict__)
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier, )

    def __str__(self):
        formatted_date = timezone.localtime(
            self.offstudy_datetime).strftime(EDC_DATETIME_FORMAT)
        return f'{self.subject_identifier} {formatted_date}'

    class Meta(VisitScheduleMetaMixin.Meta):
        abstract = True
        consent_model = None
