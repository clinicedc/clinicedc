from clinicedc_constants import NOT_APPLICABLE, NOT_EVALUATED
from demo_consent.consents import consent_v1, consent_v2
from django.contrib.sites.models import Site
from django.db import models

from edc_constants.choices import YES_NO, YES_NO_NA, YES_NO_NOT_EVALUATED
from edc_model.models import BaseUuidModel
from edc_screening.model_mixins import EligibilityModelMixin, ScreeningModelMixin
from edc_screening.screening_eligibility import ScreeningEligibility
from edc_screening.screening_identifier import (
    ScreeningIdentifier as BaseScreeningIdentifier,
)


class ScreeningIdentifier(BaseScreeningIdentifier):
    template = "S{random_string}"


class SubjectScreening(ScreeningModelMixin, EligibilityModelMixin, BaseUuidModel):
    eligibility_cls = ScreeningEligibility

    identifier_cls = ScreeningIdentifier

    consent_definitions = [consent_v1, consent_v2]

    site = models.ForeignKey(Site, on_delete=models.PROTECT, null=True, related_name="+")

    screening_consent = models.CharField(
        verbose_name=(
            "Has the subject given his/her verbal consent to be screened for the DEMO trial?"
        ),
        max_length=15,
        choices=YES_NO,
    )

    willing_to_participate = models.CharField(
        verbose_name="Is the patient willing to participate in the study if found eligible?",
        max_length=25,
        choices=YES_NO_NOT_EVALUATED,
        default=NOT_EVALUATED,
    )

    parent_guardian_consent = models.CharField(
        verbose_name=(
            "If patient is under 18, do you have consent from "
            "the parent or legal guardian to capture this information?"
        ),
        max_length=25,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text="( if 'No', STOP )",
    )

    @property
    def human_readable_identifier(self):
        """Returns a humanized screening identifier."""
        x = self.screening_identifier
        return f"{x[0:4]}-{x[4:]}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Subject Screening"
        verbose_name_plural = "Subject Screening"
