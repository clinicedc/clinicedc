from django.db import models

from edc_base.model.models import BaseUuidModel

from ..choices import VISIT_INTERVAL_UNITS
from ..classes import WindowPeriod


class BaseWindowPeriodItem(BaseUuidModel):

    """Base Model of fields that define a window period, either for visits or forms."""

    time_point = models.IntegerField(
        verbose_name="Time point",
        default=0,
    )

    base_interval = models.IntegerField(
        verbose_name="Base interval",
        help_text='Interval from base timepoint 0 as an integer.',
        default=0,
    )

    base_interval_unit = models.CharField(
        max_length=10,
        verbose_name="Base interval unit",
        choices=VISIT_INTERVAL_UNITS,
        default='D'
    )

    lower_window = models.IntegerField(
        verbose_name="Window lower bound",
        default=0,
    )

    lower_window_unit = models.CharField(
        max_length=10,
        verbose_name="Lower bound units",
        choices=VISIT_INTERVAL_UNITS,
        default='D'
    )

    upper_window = models.IntegerField(
        verbose_name="Window upper bound",
        default=0,
    )
    upper_window_unit = models.CharField(
        max_length=10,
        verbose_name="Upper bound units",
        choices=VISIT_INTERVAL_UNITS,
        default='D'
    )

    grouping = models.CharField(
        verbose_name='Grouping',
        max_length=25,
        null=True,
        blank=True,
    )

    def get_rdelta_attrname(self, unit):
        if unit == 'H':
            rdelta_attr_name = 'hours'
        elif unit == 'D':
            rdelta_attr_name = 'days'
        elif unit == 'M':
            rdelta_attr_name = 'months'
        elif unit == 'Y':
            rdelta_attr_name = 'years'
        else:
            raise TypeError('Unknown value for visit_definition.upper_window_unit. '
                            'Expected [H, D, M, Y]. Got {0}.'.format(unit))
        return rdelta_attr_name

    def is_in_window_period(self, new_datetime, reference_datetime):
        """Checks if new_datetime is within the scheduled visit window period."""
        window_period = WindowPeriod()
        return window_period.check_datetime(self, new_datetime, reference_datetime)

    class Meta:
        abstract = True
