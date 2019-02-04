from django.db import models
from django.conf import settings
from edc_base.utils import convert_php_dateformat


class Holiday(models.Model):

    country = models.CharField(max_length=25)

    local_date = models.DateField()

    name = models.CharField(max_length=25)

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

    class Meta:
        ordering = ["country", "local_date"]
        unique_together = ("country", "local_date")
