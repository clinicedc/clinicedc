from django.conf import settings
from django.db import models
from django.db.models import Index, UniqueConstraint
from django.utils.translation import gettext as _

from edc_utils import convert_php_dateformat


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

    class Meta:
        verbose_name = _("Holiday")
        verbose_name_plural = _("Holidays")
        constraints = [
            UniqueConstraint(
                fields=["country", "local_date"],
                name="%(app_label)s_%(class)s_country_uniq",
            )
        ]
        indexes = (Index(fields=["name", "country", "local_date"]),)
