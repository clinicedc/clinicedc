from django.apps import apps as django_apps
from django.db import models

from edc_base.utils import get_utcnow

from .choices import TIMEPOINT_STATUS
from .constants import OPEN_TIMEPOINT, CLOSED_TIMEPOINT, FEEDBACK
from .exceptions import TimepointError


class TimepointLookupModelMixin(models.Model):

    """Makes a model lookup the timepoint model instance on `save` and check if it is a closed
    before allowing a create or update.

    Note: the timepoint model uses the TimepointModelMixin, e.g. Appointment"""

    timepoint_lookup = None  # TimepointLookup()

    def save(self, *args, **kwargs):
        self.timepoint_lookup.raise_if_closed(self)
        super(TimepointLookupModelMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class TimepointModelMixin(models.Model):

    """Makes a model serve as a marker for a timepoint, e.g. Appointment."""

    timepoint_status = models.CharField(
        max_length=15,
        choices=TIMEPOINT_STATUS,
        default=OPEN_TIMEPOINT)

    timepoint_opened_datetime = models.DateTimeField(
        null=True,
        editable=False,
        help_text="the original calculated model's datetime, updated in the signal")

    timepoint_closed_datetime = models.DateTimeField(
        null=True,
        editable=False)

    def save(self, *args, **kwargs):
        if (kwargs.get('update_fields') != ['timepoint_status'] and
                kwargs.get('update_fields') != ['timepoint_opened_datetime', 'timepoint_status'] and
                kwargs.get('update_fields') != ['timepoint_closed_datetime', 'timepoint_status']):
            self.timepoint_open_or_raise()
        super(TimepointModelMixin, self).save(*args, **kwargs)

    def timepoint_open_or_raise(self, timepoint=None, exception_cls=None):
        app_config = django_apps.get_app_config('edc_timepoint')
        if not timepoint:
            try:
                timepoint = app_config.timepoints[self._meta.label_lower]
            except KeyError:
                raise TimepointError(
                    'Model \'{}\' is not registered in AppConfig as a timepoint. '
                    'See AppConfig for \'edc_timepoint\'.'.format(self._meta.label_lower))
        if getattr(self, timepoint.status_field) != timepoint.closed_status:
            self.timepoint_status = OPEN_TIMEPOINT
            self.timepoint_closed_datetime = None
        elif self.timepoint_status == CLOSED_TIMEPOINT:
            raise TimepointError(
                'This \'{}\' instance is closed for data entry. See Timpoint.'.format(self._meta.verbose_name))
        return True

    def timepoint_close_timepoint(self):
        """Closes a timepoint."""
        app_config = django_apps.get_app_config('edc_timepoint')
        timepoint = app_config.timepoints[self._meta.label_lower]
        if getattr(self, timepoint.status_field) == timepoint.closed_status:
            self.timepoint_status = CLOSED_TIMEPOINT
            self.timepoint_closed_datetime = get_utcnow()
            self.save(update_fields=['timepoint_status'])

    def timepoint_open_timepoint(self):
        """Re-opens a timepoint."""
        if self.timepoint_status == CLOSED_TIMEPOINT:
            self.timepoint_status = OPEN_TIMEPOINT
            self.timepoint_closed_datetime = None
            self.save(update_fields=['timepoint_closed_datetime', 'timepoint_status'])

    def timepoint(self):
        """Formats and returns the status for the change_list."""
        if self.timepoint_status == OPEN_TIMEPOINT:
            return '<span style="color:green;">Open</span>'
        elif self.timepoint_status == CLOSED_TIMEPOINT:
            return '<span style="color:red;">Closed</span>'
        elif self.timepoint_status == FEEDBACK:
            return '<span style="color:orange;">Feedback</span>'
    timepoint.allow_tags = True

    class Meta:
        abstract = True
