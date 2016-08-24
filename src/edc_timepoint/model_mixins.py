from django.apps import apps as django_apps
from django.db import models

from .choices import TIMEPOINT_STATUS
from .constants import OPEN_TIMEPOINT, CLOSED_TIMEPOINT, FEEDBACK
from django.utils import timezone


class TimepointStatusError(Exception):
    pass


class TimepointStatusMixin(models.Model):

    # this is the original calculated appointment datetime
    # updated in the signal
    timepoint_opened_datetime = models.DateTimeField(
        verbose_name=("Time point"),
        help_text="calculated timepoint datetime. Do not change",
        null=True,
        editable=False)

    timepoint_status = models.CharField(
        max_length=15,
        choices=TIMEPOINT_STATUS,
        default=OPEN_TIMEPOINT)

    timepoint_closed_datetime = models.DateTimeField(
        verbose_name='Date timepoint closed.',
        null=True,
        blank=True)

    def save(self, *args, **kwargs):
        if (kwargs.get('update_fields') != ['timepoint_status'] and
                kwargs.get('update_fields') != ['timepoint_opened_datetime', 'timepoint_status']):
            app_config = django_apps.get_app_config('edc_timepoint')
            attrs = app_config.timepoint_models[self._meta.label_lower]
            if getattr(self, attrs['status_field']) != attrs['closed_status']:
                self.timepoint_status = OPEN_TIMEPOINT
                self.timepoint_closed_datetime = None
            elif self.timepoint_status == CLOSED_TIMEPOINT:
                raise TimepointStatusError('Model is closed for data entry. See TimpointStatus.')
        super(TimepointStatusMixin, self).save(*args, **kwargs)

    def close_timepoint(self):
        app_config = django_apps.get_app_config('edc_timepoint')
        attrs = app_config.timepoint_models[self._meta.label_lower]
        if getattr(self, attrs['status_field']) == attrs['closed_status']:
            self.timepoint_status = CLOSED_TIMEPOINT
            self.timepoint_closed_datetime = timezone.now()
            self.save(update_fields=['timepoint_status'])

    def timepoint(self):
        """Formats and returns the status for the dashboard."""
        if self.timepoint_status == OPEN_TIMEPOINT:
            return '<span style="color:green;">Open</span>'
        elif self.timepoint_status == CLOSED_TIMEPOINT:
            return '<span style="color:red;">Closed</span>'
        elif self.timepoint_status == FEEDBACK:
            return '<span style="color:orange;">Feedback</span>'
    timepoint.allow_tags = True

    class Meta:
        abstract = True
