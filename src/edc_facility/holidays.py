import arrow
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


class HolidayError(Exception):
    pass


class Holidays:

    """A class used by Facility to get holidays for the
    country of facility.
    """

    model = "edc_facility.holiday"

    def __init__(self, country=None, facility_name=None):
        self._holidays = {}
        self.country = country
        if not self.country:
            try:
                self.country = settings.COUNTRY
            except AttributeError:
                pass
            if not self.country:
                raise HolidayError(
                    f"No country specified for facility {facility_name}. "
                    f"See settings.COUNTRY"
                )
        self.time_zone = settings.TIME_ZONE
        self.model_cls = django_apps.get_model(self.model)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(country={self.country}, "
            f"time_zone={self.time_zone})"
        )

    def __len__(self):
        return len(self.holidays)

    @property
    def local_dates(self):
        return [obj.local_date for obj in self.holidays]

    @property
    def holidays(self):
        """Returns a dictionary of holidays for this country as
        {local_date: label, ...}.
        """
        if not self._holidays:
            self._holidays = self.model_cls.objects.filter(country=self.country)
            if not self._holidays:
                raise HolidayError(
                    f"No holidays found for '{self.country}. See {self.model}."
                )
        return self._holidays

    def is_holiday(self, utc_datetime=None):
        """Returns True if the UTC datetime is a holiday.
        """
        local_date = self.local_date(utc_datetime=utc_datetime)
        try:
            self.holidays.get(country=self.country, local_date=local_date)
        except ObjectDoesNotExist:
            return False
        return True

    def local_date(self, utc_datetime=None):
        """Returns the localized date from UTC.
        """
        utc = arrow.Arrow.fromdatetime(utc_datetime)
        return utc.to(self.time_zone).date()
