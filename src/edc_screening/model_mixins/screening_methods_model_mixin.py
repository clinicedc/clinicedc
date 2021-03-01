from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import models
from edc_utils.date import get_utcnow

from ..stubs import SubjectScreeningModelStub


class ScreeningMethodsModeMixin(models.Model):
    def __str__(self: SubjectScreeningModelStub):
        return f"{self.screening_identifier} {self.gender} {self.age_in_years}"

    def natural_key(self: SubjectScreeningModelStub):
        return tuple(self.screening_identifier)

    @staticmethod
    def get_search_slug_fields():
        return ["screening_identifier", "subject_identifier", "reference"]

    @property
    def estimated_dob(self: SubjectScreeningModelStub) -> date:
        return get_utcnow().date() - relativedelta(years=self.age_in_years)

    class Meta:
        abstract = True
