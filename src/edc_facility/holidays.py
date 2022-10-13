from datetime import date

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from edc_utils.date import to_local

from .exceptions import HolidayError
from .holidays_disabled import holidays_disabled


class Holidays:

    """A class used by Facility to get holidays for the
    country of facility.
    """

    model = "edc_facility.holiday"

    def __init__(self) -> None:
        if getattr(settings, "COUNTRY", None):
            raise HolidayError(
                "COUNTRY is no longer a valid settings attribute. "
                "Country is determined from the site definition "
                "in your project`s sites app. See SingleSite and "
                "SiteProfile in edc-sites."
            )
        self._country = None
        self._holidays = None
        self.model_cls = django_apps.get_model(self.model)
        self.site_model_cls = django_apps.get_model("sites.site")

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(country={self.country}, "
            f"time_zone={settings.TIME_ZONE})"
        )

    def __len__(self):
        return self.holidays.count()

    @property
    def country(self) -> str:
        if not self._country:
            self._country = self.site_model_cls.objects.get_current().siteprofile.country
            if not self._country:
                raise HolidayError(
                    f"Country not defined for site. Got site="
                    f"`{self.site_model_cls.objects.get_current()}`"
                )
        return self._country

    @property
    def local_dates(self) -> list[date]:
        return [obj.local_date for obj in self.holidays]

    @property
    def holidays(self) -> QuerySet:
        """Returns a holiday model instance for this country."""
        if not self._holidays:
            if holidays_disabled():
                self._holidays = self.model_cls.objects.none()
            else:
                self._holidays = self.model_cls.objects.filter(country=self.country)
                if not self._holidays:
                    raise HolidayError(
                        f"No holidays found for '{self.country}. See {self.model}."
                    )
        return self._holidays

    def is_holiday(self, utc_datetime=None) -> bool:
        """Returns True if the UTC datetime is a holiday."""
        local_date = to_local(utc_datetime).date()
        try:
            self.model_cls.objects.get(country=self.country, local_date=local_date)
        except ObjectDoesNotExist:
            return False
        return True
