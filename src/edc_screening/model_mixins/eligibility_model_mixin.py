from django.db import models
from edc_utils import get_utcnow

from ..screening_eligibility import ScreeningEligibility, ScreeningEligibilityError
from ..stubs import SubjectScreeningModelStub


class EligibilityModelMixin(models.Model):

    eligibility_cls = ScreeningEligibility

    eligible = models.BooleanField(default=False, editable=False)

    reasons_ineligible = models.TextField(
        verbose_name="Reason not eligible", max_length=150, null=True, editable=False
    )

    eligibility_datetime = models.DateTimeField(
        null=True,
        editable=False,
        help_text="Date and time eligibility was determined relative to report_datetime",
    )

    real_eligibility_datetime = models.DateTimeField(
        null=True,
        editable=False,
        help_text="Date and time eligibility was determined relative to now",
    )

    def save(self: SubjectScreeningModelStub, *args, **kwargs):
        """When saved, the eligibility_cls is instantiated and the
        value of `eligible` is evaluated.

        * If not eligible, updates reasons_ineligible.
        * Screening Identifier is always allocated.
        """
        eligibility_obj = self.eligibility_cls(model_obj=self, allow_none=True)
        self.eligible = eligibility_obj.eligible
        self.reasons_ineligible = eligibility_obj.reasons_ineligible

        if (not self.eligible and not self.reasons_ineligible) or (
            self.eligible and self.reasons_ineligible
        ):
            raise ScreeningEligibilityError(
                f"Invalid combination. Cannot have eligible={self.eligible} "
                f"and reasons_ineligible={self.reasons_ineligible}."
            )
        elif not self.eligible and self.reasons_ineligible:
            reasons_ineligible = [v for v in self.reasons_ineligible.values() if v]
            reasons_ineligible.sort()
            self.reasons_ineligible = "|".join(reasons_ineligible)
        else:
            self.reasons_ineligible = None
        if not self.id:
            self.screening_identifier = self.identifier_cls().identifier
        if self.eligible:
            self.eligibility_datetime = self.report_datetime
            self.real_eligibility_datetime = get_utcnow()
        else:
            self.eligibility_datetime = None
            self.real_eligibility_datetime = None
        super().save(*args, **kwargs)  # type:ignore

    class Meta:
        abstract = True
