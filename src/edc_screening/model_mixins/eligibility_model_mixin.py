from django.db import models

from ..screening_eligibility import ScreeningEligibility


class EligibilityModelMixin(models.Model):

    eligibility_cls = ScreeningEligibility

    def save(self, *args, **kwargs):
        """When saved, the eligibility_cls is instantiated and the
        value of `eligible` is evaluated.

        * If not eligible, updates reasons_ineligible.
        * Screening Identifier is always allocated.
        """
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

    class Meta:
        abstract = True
