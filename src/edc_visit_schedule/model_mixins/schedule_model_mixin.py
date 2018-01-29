from django.conf import settings
from django.db import models
from django.utils import timezone
from edc_base import convert_php_dateformat
from edc_base.model_managers import HistoricalRecords
from edc_base.sites import CurrentSiteManager, SiteModelMixin
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_identifier.managers import SubjectIdentifierManager


class ScheduleModelMixin(UniqueSubjectIdentifierFieldMixin, SiteModelMixin, models.Model):
    """A model mixin for a schedule's on/off schedule models.
    """
    report_datetime = models.DateTimeField(editable=False)

    on_site = CurrentSiteManager()

    objects = SubjectIdentifierManager()

    history = HistoricalRecords()

    def __str__(self):
        formatted_date = timezone.localtime(
            self.report_datetime).strftime(
                convert_php_dateformat(settings.SHORT_DATE_FORMAT))
        return f'{self.subject_identifier} {formatted_date}'

    def natural_key(self):
        return (self.subject_identifier, )
    natural_key.dependencies = ['sites.Site']

    class Meta:
        abstract = True
