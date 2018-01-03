from django.conf import settings
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.utils import timezone
from edc_base import convert_php_dateformat
from edc_base.model_managers import HistoricalRecords
from edc_base.sites.site_model_mixin import SiteModelMixin
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_identifier.managers import SubjectIdentifierManager


class ScheduleModelMixin(UniqueSubjectIdentifierFieldMixin, SiteModelMixin, models.Model):
    """A model mixin for a schedule's on/off schedule models.
    """
    report_datetime = models.DateTimeField(editable=False)

    objects = SubjectIdentifierManager()

    history = HistoricalRecords()

    on_site = CurrentSiteManager()

    def __str__(self):
        formatted_date = timezone.localtime(
            self.report_datetime).strftime(
                convert_php_dateformat(settings.SHORT_DATE_FORMAT))
        return f'{self.subject_identifier} {formatted_date}'

    def save(self, *args, **kwargs):
        self.report_datetime = self.onschedule_datetime
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier, )

    class Meta:
        abstract = True
