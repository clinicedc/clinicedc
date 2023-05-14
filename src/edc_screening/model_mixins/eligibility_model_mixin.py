from django.db import models
from edc_utils import get_utcnow

from ..screening_eligibility import ScreeningEligibility
from ..stubs import SubjectScreeningModelStub


class EligibilityFieldsModelMixin(models.Model):
    eligible = models.BooleanField(default=False)

    reasons_ineligible = models.TextField(
        verbose_name="Reason not eligible", max_length=150, null=True
    )

    eligibility_datetime = models.DateTimeField(
        null=True,
        help_text="Date and time eligibility was determined relative to report_datetime",
    )

    real_eligibility_datetime = models.DateTimeField(
        null=True,
        help_text="Date and time eligibility was determined relative to now",
    )

    def get_report_datetime_for_eligibility_datetime(self):
        """Returns report_datetime.

        Override to use a different report_datetime if, for example,
        screening is done in more than one part.
        """
        return self.report_datetime

    class Meta:
        abstract = True


class EligibilityModelMixin(EligibilityFieldsModelMixin, models.Model):
    eligibility_cls = ScreeningEligibility

    def save(self: SubjectScreeningModelStub, *args, **kwargs):
        """When saved, the eligibility_cls is instantiated and the
        value of `eligible` is evaluated.

        * If not eligible, updates reasons_ineligible.
        * Screening Identifier is always allocated.
        """
        # if self.eligibility_cls:
        self.eligibility_cls(model_obj=self)
        # self.eligible = eligibility_obj.is_eligible
        # self.reasons_ineligible = eligibility_obj.reasons_ineligible
        if not self.id:
            self.screening_identifier = self.identifier_cls().identifier
        if self.eligible:
            self.eligibility_datetime = self.get_report_datetime_for_eligibility_datetime()
            self.real_eligibility_datetime = get_utcnow()
        else:
            self.eligibility_datetime = None
            self.real_eligibility_datetime = None
        super().save(*args, **kwargs)  # type:ignore

    class Meta:
        abstract = True
