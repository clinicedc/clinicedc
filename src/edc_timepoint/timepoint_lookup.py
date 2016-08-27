from django.apps import apps as django_apps
from edc_timepoint.constants import CLOSED_TIMEPOINT
from edc_timepoint.exceptions import TimepointError


class TimepointLookup:

    def __init__(self, timepoint_model, lookup):
        self.timepoint_model = '.'.join(timepoint_model.split('.'))  # label_lower format
        self.lookup = lookup

    def __str__(self):
        return self.timepoint_model

    def raise_if_closed(self, instance, exception_cls=None):
        exception_cls = exception_cls or TimepointError
        app_config = django_apps.get_app_config('edc_timepoint')
        timepoint_config = app_config.timepoints[self.timepoint_model]
        try:
            timepoint = timepoint_config.model.objects.get(
                **{self.lookup: CLOSED_TIMEPOINT})
            raise exception_cls(
                'Model cannot be modified. Timepoint is closed. See {}.'.format(timepoint))
        except timepoint_config.model.DoesNotExist:
            pass
