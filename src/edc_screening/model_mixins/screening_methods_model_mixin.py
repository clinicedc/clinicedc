from dateutil.relativedelta import relativedelta
from django.db import models
from edc_utils.date import get_utcnow


class ScreeningMethodsModeMixin(models.Model):
    def __str__(self):
        return f"{self.screening_identifier} {self.gender} {self.age_in_years}"

    def natural_key(self):
        return (self.screening_identifier,)

    def get_search_slug_fields(self):
        return ["screening_identifier", "subject_identifier", "reference"]

    @property
    def estimated_dob(self):
        return get_utcnow().date() - relativedelta(years=self.age_in_years)

    class Meta:
        abstract = True
