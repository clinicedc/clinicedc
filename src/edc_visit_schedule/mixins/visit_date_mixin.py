from dateutil.relativedelta import relativedelta


class VisitDateMixin(object):
    """Class to manage an appointment's or visit's window period.

    An appointment datetime must fall within the date range determined by the lower and upper bounds set in the visit definition.
    """
    def verify_datetime(self, new_datetime, reference_datetime):
        """Same as is_datetime_in_window but raises an exception if false."""
        if not self.is_datetime_in_window(new_datetime, reference_datetime):
            raise ValueError('Date does not fall within the configured window period for this visit.')

    def is_datetime_in_window(self, new_datetime, reference_datetime):
        """Checks if new_datetime is within the scheduled visit window period.

        Args:
            reference_datetime: auto calculated / optimal timepoint datetime (best_appt_datetime)
            new_datetime: user suggested datetime.
        """
        diff = 0  # always in days for now
        retval = True
        self.error = None
        self.error_message = None
        self.new_datetime = new_datetime
        self.reference_datetime = reference_datetime

        if not reference_datetime:
            raise TypeError(
                'Parameter \'reference_datetime\' cannot be None. Is appointment.best_appt_datetime = None?')

        if self.upper_tdelta.days > 0:
            # past upper window boundary
            unit = self.upper_unit
            window_value = self.upper_window
            td_from_boundary = self.upper_tdelta
            window_name = 'upper'
        elif self.lower_tdelta.days < 0:
            # past lower window boundary
            unit = self.lower_unit
            window_value = self.lower_window
            td_from_boundary = self.lower_tdelta  # was being set to upper??
            window_name = 'lower'
        elif self.lower_tdelta.days >= 0 and self.upper_tdelta.days <= 0:
            # within window period
            unit = None
            window_value = None
            td_from_boundary = None
            window_name = None
            diff = 0
        if td_from_boundary:
            diff = td_from_boundary.days  # TODO: this cannot be in days if unit is Hours
            retval = False
            self.error = True
            self.error_message = (
                'Datetime is out of {window_name} window period. Expected a datetime between {lower} and {upper}.'
                'Window allows {window_value} {unit}. Got {diff}.'.format(
                    lower=self.lower_window_datetime,
                    upper=self.upper_window_datetime,
                    window_name=window_name,
                    window_value=window_value,
                    unit=unit,
                    diff=diff))
        return retval

    @property
    def upper_window_datetime(self):
        """Returns the actual datetime for the window's
        upper boundary relative to new_appt_datetime."""
        rdelta = relativedelta()
        setattr(
            rdelta,
            self.get_rdelta_attrname(
                self.upper_window_unit),
            self.upper_window
        )
        return self.reference_datetime + rdelta

    @property
    def lower_window_datetime(self):
        """Returns the actual datetime for the window's
        lower boundary relative to new_appt_datetime."""
        rdelta = relativedelta()
        setattr(
            rdelta,
            self.get_rdelta_attrname(
                self.lower_window_unit),
            self.lower_window
        )
        return self.reference_datetime - rdelta

    @property
    def upper_tdelta(self):
        """Calculates and returns the timedelta between proposed date and the upper date."""
        return self.new_datetime - self.upper_window_datetime

    @property
    def lower_tdelta(self):
        """Calculates and returns the timedelta between proposed date and the lower date."""
        return self.new_datetime - self.lower_window_datetime

    @property
    def upper_unit(self):
        """Returns units for upper boundary as defined in visit definition."""
        return self.get_rdelta_attrname(self.upper_window_unit)

    @property
    def lower_unit(self):
        """Returns units for lower boundary as defined in visit definition."""
        return self.get_rdelta_attrname(self.lower_window_unit)
