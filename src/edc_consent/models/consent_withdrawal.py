from clinicedc_constants import NULL_STRING
from django.db import models

from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_model_fields.fields import OtherCharField
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow

from .list_models import CeasedConsentOptions, RetainedConsentOptions

TRIGGERS = (
    "Participant Decision (Voluntary Withdrawal)",
    "Investigator Decision (Adverse Event / Safety)",
    "Sponsor Decision (Study Termination)",
    "Protocol-Defined Criterion Met",
)


# SCOPE_CEASED = (
# [SECTION 2: SCOPE OF CESSATION (What Ceases)]
# ├── Question 1: Intervention Status
# │   └── Cease Study Intervention / IP? [ Yes / No / Not Applicable ]
# │       └── Date Last Dose/Intervention Received: [ Date ]
# │
# └── Question 2: Primary Study Activity Status
#     └── Cease In-Person Study Visits & Protocol Procedures? [ Yes / No ]
# )
# SCOPE_RETAINED = (
# [SECTION 3: SCOPE OF RETAINED CONSENT (What Continues)]
# └── Question 3: Permitted Follow-Up & Data Processing (Multi-Select or Tiered Radio)
#   ├── Level A: Direct Contact Only (Phone/Email/Surveys for vital status & outcomes)
#   ├── Level B: Passive Outcome Tracking Only (EHR/Medical records access, registry linkage)
#   ├── Level C: End-of-Study Results Communication Only (Notify participant of trial findings)
#   └── Level D: Complete Cessation of All Follow-up (No direct or indirect contact permitted)
# )
#
# level of participation they want to have and what they want to cease
#
# The meaning can range
# stop receiving the study intervention
# stop attending study visits in person (but
# perhaps be happy to be contacted or for information
# about their health outcomes to be collected from
# their regular doctors or from routine health data
# systems) to having their biological samples no
# longer assayed or stored or their data no longer
# being processed or shared.


class ConsentWithdrawal(
    SiteModelMixin,
    UniqueSubjectIdentifierFieldMixin,
    BaseUuidModel,
):
    """A user form to declare that the subject has withdrawn consent
    for further followup.

    References
    ----------
    .. [WHO2024] World Health Organization. (2024). *Guidance for best practices
       for clinical trials*. Geneva: World Health Organization.
       https://iris.who.int/items/27529498-7904-404f-9a53-e80977c953a8

       see 2.2.3 Changing consent
    """

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time", default=get_utcnow
    )

    intent_communication_method = models.CharField(
        verbose_name="How did the participant communicate their intention to change consent?",
        max_length=50,
        choices=(),
    )

    intent_datetime = models.DateTimeField(
        verbose_name="When did the subject communicated their intention to change consent?",
        default=get_utcnow,
    )

    scope_of_cessation = models.ManyToManyField(
        CeasedConsentOptions,
        verbose_name="Which aspects of consent does the participant wish to cease",
    )

    scope_of_cessation_consent_other = OtherCharField(help_text="other scope of cessation")

    scope_of_retained_consent = models.ManyToManyField(
        RetainedConsentOptions,
        verbose_name="Which aspects of consent does the participant wish to retain",
    )

    scope_of_retained_consent_other = OtherCharField(
        help_text="other scope of retained_consent"
    )

    consent_change_reason = models.TextField(
        verbose_name="If possible, briefly summarize the participant's communication?",
        max_length=500,
        default=NULL_STRING,
        blank=True,
        help_text="May be left blank",
    )

    # Describe the level of participation wishes to cease
    # - follow-up
    # level_of_participation
    #
    """
    need something about the intention. May we continue to use the data??
    - is this just about follow-up or more??
    - may we still contact them?
    - what are the components of a consent?
    - specifically what does the participant wish to cease?
    See WHO 2024 Guidance for best practices for clinical trials: 2.2.3 Changing consent
    """

    class Meta(BaseUuidModel):
        verbose_name = "Consent withdrawal"
        verbose_name_plural = "Consent withdrawal"
