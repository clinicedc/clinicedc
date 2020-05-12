from django.conf import settings
from django.core.checks import Warning
from django.db import models
from django.db.utils import ProgrammingError, OperationalError
from edc_sites import get_current_country
from edc_utils import convert_php_dateformat


class Holiday(models.Model):

    country = models.CharField(max_length=50)

    local_date = models.DateField()

    name = models.CharField(max_length=50)

    @property
    def label(self):
        return self.name

    @property
    def formatted_date(self):
        return self.local_date.strftime(
            convert_php_dateformat(settings.SHORT_DATE_FORMAT)
        )

    def __str__(self):
        return f"{self.label} on {self.formatted_date}"

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        try:
            if cls.objects.all().count() == 0:
                errors.append(
                    Warning(
                        "Holiday table is empty. Run management command 'import_holidays'. "
                        "See edc_facility.Holidays",
                        id="edc_facility.003",
                    )
                )
            elif cls.objects.filter(country=get_current_country()).count() == 0:
                countries = [obj.country for obj in cls.objects.all()]
                countries = list(set(countries))
                errors.append(
                    Warning(
                        f"No Holidays have been defined for this country. "
                        f"See edc_facility.Holidays. Expected one of {countries}. "
                        f"Got country='{get_current_country()}'",
                        id="edc_facility.004",
                    )
                )
        except (ProgrammingError, OperationalError):
            pass
        return errors

    class Meta:
        ordering = ["country", "local_date"]
        unique_together = ("country", "local_date")
