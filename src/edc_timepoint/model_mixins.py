from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from edc_utils import get_utcnow

from .choices import TIMEPOINT_STATUS
from .constants import CLOSED_TIMEPOINT, FEEDBACK, OPEN_TIMEPOINT
from .timepoint import TimepointClosed
from .timepoint_collection import TimepointConfigError
from .timepoint_lookup import TimepointLookup
from .utils import get_enable_timepoint_checks


class UnableToCloseTimepoint(Exception):
    pass


class TimepointLookupModelMixin(models.Model):

    """Makes a model lookup the timepoint model instance on `save`
    and check if it is a closed before allowing a create or update.

    Note: the timepoint model uses the TimepointModelMixin, e.g. Appointment
    """

    timepoint_lookup_cls = TimepointLookup

    def save(self, *args, **kwargs):
        timepoint_lookup_cls = getattr(self, "timepoint_lookup_cls", None)
        if timepoint_lookup_cls and get_enable_timepoint_checks():
            timepoint_lookup = self.timepoint_lookup_cls()
            if timepoint_lookup.timepoint_model == self._meta.label_lower:
                raise ImproperlyConfigured(
                    f"Timepoint model cannot use TimepointLookupModelMixin. "
                    f"Got {self._meta.label_lower}"
                )
            timepoint_lookup.raise_if_closed(model_obj=self)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class TimepointModelMixin(models.Model):

    """Makes a model serve as a marker for a timepoint, e.g. Appointment."""

    enabled_as_timepoint = True

    timepoint_status = models.CharField(
        max_length=15, choices=TIMEPOINT_STATUS, default=OPEN_TIMEPOINT
    )

    timepoint_opened_datetime = models.DateTimeField(
        null=True,
        editable=False,
        help_text="the original calculated model's datetime, updated in the signal",
    )

    timepoint_closed_datetime = models.DateTimeField(null=True, editable=False)

    def save(self, *args, **kwargs):
        if self.enabled_as_timepoint:
            if (
                kwargs.get("update_fields") != ["timepoint_status"]
                and kwargs.get("update_fields")
                != ["timepoint_opened_datetime", "timepoint_status"]
                and kwargs.get("update_fields")
                != ["timepoint_closed_datetime", "timepoint_status"]
            ):
                self.timepoint_open_or_raise()
        super().save(*args, **kwargs)

    def update_timepoint(self):
        """Called by signal"""
        if self.enabled_as_timepoint:
            app_config = django_apps.get_app_config("edc_timepoint")
            if "historical" not in self._meta.label_lower:
                timepoint = app_config.timepoints.get(self._meta.label_lower)
                datetime_value = getattr(self, timepoint.datetime_field)
                if (
                    self.timepoint_opened_datetime is None
                    or self.timepoint_opened_datetime != datetime_value
                ):
                    self.timepoint_opened_datetime = datetime_value
                    self.timepoint_status = OPEN_TIMEPOINT
                    self.save_base(
                        update_fields=[
                            "timepoint_opened_datetime",
                            "timepoint_status",
                        ]
                    )

    def timepoint_open_or_raise(self, timepoint=None):
        if not timepoint:
            app_config = django_apps.get_app_config("edc_timepoint")
            try:
                timepoint = app_config.timepoints.get(self._meta.label_lower)
            except KeyError:
                raise TimepointConfigError(
                    f"Model '{self._meta.label_lower}' is not registered "
                    f"in AppConfig as a timepoint. "
                    f"See AppConfig for 'edc_timepoint'."
                )
        if getattr(self, timepoint.status_field) != timepoint.closed_status:
            self.timepoint_status = OPEN_TIMEPOINT
            self.timepoint_closed_datetime = None
        elif self.timepoint_status == CLOSED_TIMEPOINT:
            raise TimepointClosed(
                f"This '{self._meta.verbose_name}' instance is closed "
                f"for data entry. See Timepoint."
            )
        return True

    def timepoint_close_timepoint(self):
        """Closes a timepoint.

        Updates the timepoint specific fields when the status field
        changes to closed.
        """
        app_config = django_apps.get_app_config("edc_timepoint")
        timepoint = app_config.timepoints.get(self._meta.label_lower)
        status = getattr(self, timepoint.status_field)
        if status == timepoint.closed_status:
            self.timepoint_status = CLOSED_TIMEPOINT
            self.timepoint_closed_datetime = get_utcnow()
            self.save(update_fields=["timepoint_status"])
        else:
            raise UnableToCloseTimepoint(
                f"Unable to close timepoint. Got {self._meta.label_lower}."
                f"{timepoint.status_field} != {timepoint.closed_status}. "
                f"Got '{status}'."
            )

    def timepoint_open_timepoint(self):
        """Re-opens a timepoint."""
        if self.timepoint_status == CLOSED_TIMEPOINT:
            self.timepoint_status = OPEN_TIMEPOINT
            self.timepoint_closed_datetime = None
            self.save(update_fields=["timepoint_closed_datetime", "timepoint_status"])

    def timepoint(self):
        """Formats and returns the status for the change_list."""
        if self.timepoint_status == OPEN_TIMEPOINT:
            return '<span style="color:green;">Open</span>'
        elif self.timepoint_status == CLOSED_TIMEPOINT:
            return '<span style="color:red;">Closed</span>'
        elif self.timepoint_status == FEEDBACK:
            return '<span style="color:orange;">Feedback</span>'

    # timepoint.allow_tags = True

    class Meta:
        abstract = True
