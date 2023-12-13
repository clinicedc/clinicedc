import sys
from typing import List

from django.conf import settings
from django.core.checks import Warning
from django.db import models
from django.db.models import Index, UniqueConstraint
from django.db.utils import OperationalError, ProgrammingError
from django.utils.translation import gettext as _
from edc_sites.site import sites
from edc_utils import convert_php_dateformat

from ..holidays_disabled import holidays_disabled


class Holiday(models.Model):
    id = models.BigAutoField(primary_key=True)

    country = models.CharField(max_length=50)

    local_date = models.DateField()

    name = models.CharField(max_length=50)

    @property
    def label(self) -> str:
        return self.name

    @property
    def formatted_date(self) -> str:
        return self.local_date.strftime(convert_php_dateformat(settings.SHORT_DATE_FORMAT))

    def __str__(self):
        return f"{self.label} on {self.formatted_date}"

    @classmethod
    def check(cls, **kwargs) -> List[Warning]:
        errors = super().check(**kwargs)
        if "makemigrations" not in sys.argv and "migrate" not in sys.argv:
            if not holidays_disabled():
                try:
                    if cls.objects.all().count() == 0:
                        errors.append(
                            Warning(
                                "Holiday table is empty. Run management command "
                                "'import_holidays'. See edc_facility.Holidays",
                                id="edc_facility.003",
                            )
                        )
                    elif cls.objects.filter(country=sites.get_current_country()).count() == 0:
                        countries = [obj.country for obj in cls.objects.all()]
                        countries = list(set(countries))
                        errors.append(
                            Warning(
                                f"No Holidays have been defined for this country. "
                                f"See edc_facility.Holidays. Expected one of {countries}. "
                                f"Got country='{sites.get_current_country()}'",
                                id="edc_facility.004",
                            )
                        )
                except (ProgrammingError, OperationalError):
                    pass
        return errors

    class Meta:
        verbose_name = _("Holiday")
        verbose_name_plural = _("Holidays")
        constraints = [
            UniqueConstraint(
                fields=["country", "local_date"], name="%(app_label)s_%(class)s_country_uniq"
            )
        ]
        indexes = [Index(fields=["name", "country", "local_date"])]
