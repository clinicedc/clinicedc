from datetime import date
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.db import models

from ..stubs import SubjectScreeningModelStub


class ScreeningMethodsModeMixin(models.Model):
    def __str__(self: SubjectScreeningModelStub):
        return f"{self.screening_identifier} {self.gender} {self.age_in_years}"

    def natural_key(self: SubjectScreeningModelStub):
        return (self.screening_identifier,)  # noqa

    @staticmethod
    def get_search_slug_fields():
        return ["screening_identifier", "subject_identifier", "reference"]

    @property
    def estimated_dob(self: SubjectScreeningModelStub) -> date:
        return self.report_datetime.astimezone(ZoneInfo("UTC")).date() - relativedelta(
            years=self.age_in_years
        )

    class Meta:
        abstract = True
