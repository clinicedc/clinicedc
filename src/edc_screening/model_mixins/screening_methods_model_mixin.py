from dateutil.relativedelta import relativedelta
from django.db import models
from edc_utils.date import get_utcnow

from ..screening_identifier import ScreeningIdentifier
from ..screening_eligibility import ScreeningEligibility


class ScreeningMethodsModeMixin(models.Model):

    eligibility_cls = ScreeningEligibility

    identifier_cls = ScreeningIdentifier

    def __str__(self):
        return f"{self.screening_identifier} {self.gender} {self.age_in_years}"

    def save(self, *args, **kwargs):
        eligibility_obj = self.eligibility_cls(model_obj=self, allow_none=True)
        self.eligible = eligibility_obj.eligible
        if not self.eligible:
            reasons_ineligible = [
                v for v in eligibility_obj.reasons_ineligible.values() if v
            ]
            reasons_ineligible.sort()
            self.reasons_ineligible = "|".join(reasons_ineligible)
        else:
            self.reasons_ineligible = None
        if not self.id:
            self.screening_identifier = self.identifier_cls().identifier
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.screening_identifier,)

    def get_search_slug_fields(self):
        return ["screening_identifier", "subject_identifier", "reference"]

    @property
    def estimated_dob(self):
        return get_utcnow().date() - relativedelta(years=self.age_in_years)

    class Meta:
        abstract = True
