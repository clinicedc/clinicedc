from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from multisite.exceptions import MultisiteSiteDoesNotExist

from edc_sites.site import sites as site_sites
from edc_sites.utils import get_site_model_cls
from edc_utils.date import to_local

from .exceptions import FacilityCountryError, FacilitySiteError, HolidayError
from .holidays_disabled import holidays_disabled

if TYPE_CHECKING:
    from django.contrib.sites.models import Site


class Holidays:
    """A class used by Facility to get holidays for the
    country of facility.
    """

    model: str = "edc_facility.holiday"

    def __init__(self, site: Site = None) -> None:
        self._holidays = None
        self.model_cls = django_apps.get_model(self.model)
        self._site: Site | None = site

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(country={self.country}, "
            f"time_zone={settings.TIME_ZONE})"
        )

    def __len__(self):
        return self.holidays.count()

    @property
    def local_dates(self) -> list[date]:
        return [obj.local_date for obj in self.holidays]

    @property
    def site(self) -> Site | None:
        """Returns the Site model instance."""
        if not self._site:
            try:
                self._site = get_site_model_cls().objects.get_current()
            except ObjectDoesNotExist as e:
                raise FacilitySiteError(
                    f"Unable to determine site. Cannot lookup holidays. "
                    f"settings.SITE_ID={settings.SITE_ID}. Got {e}"
                )
            except MultisiteSiteDoesNotExist as e:
                raise FacilitySiteError(
                    f"Unable to determine site. Cannot lookup holidays. "
                    f"settings.SITE_ID={settings.SITE_ID}. Got MultisiteSiteDoesNotExist({e})."
                )
        return self._site

    @property
    def country(self) -> str:
        """Returns country string.

        Requires SiteProfile from edc_sites to be updated.
        """
        country = site_sites.get(self.site.id).country
        if not country:
            raise FacilityCountryError("Unable to determine country.")
        return country

    @property
    def holidays(self) -> QuerySet:
        """Returns a holiday model instance for this country."""
        if not self._holidays:
            if holidays_disabled():
                self._holidays = self.model_cls.objects.none()
            elif not self.model_cls.objects.filter(country=self.country).exists():
                raise HolidayError(f"No holidays found for '{self.country}. See {self.model}.")
            self._holidays = self.model_cls.objects.filter(country=self.country)
        return self._holidays

    def is_holiday(self, utc_datetime=None) -> bool:
        """Returns True if the UTC datetime is a holiday."""
        local_date = to_local(utc_datetime).date()
        try:
            self.model_cls.objects.get(country=self.country, local_date=local_date)
        except ObjectDoesNotExist:
            return False
        return True
