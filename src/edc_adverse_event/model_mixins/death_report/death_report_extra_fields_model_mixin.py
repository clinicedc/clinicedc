from django.db import models
from edc_constants.choices import YES_NO
from edc_model.models import OtherCharField

from ...choices import CONTACT, DEATH_LOCATIONS, INFORMANT


class DeathReportExtraFieldsModelMixin(models.Model):

    """Additional fields for the Death Report model.

    Declare with from `DeathReportModelMixin` from `edc_adverse_event`.
    """

    death_location = models.CharField(
        verbose_name="Where did the participant die?",
        max_length=50,
        choices=DEATH_LOCATIONS,
    )

    death_location_other = OtherCharField()

    hospital_death = models.CharField(
        verbose_name=(
            "Did the participant die in hospital, or die just after " "visiting a hospital?"
        ),
        max_length=50,
        choices=YES_NO,
    )

    hospital_name = models.CharField(
        verbose_name="Which hospital was this", max_length=50, null=True, blank=True
    )

    informant = models.CharField(
        verbose_name="Who has confirmed that the participant has died?",
        max_length=50,
        choices=INFORMANT,
    )

    informant_other = OtherCharField()

    confirmed_by = models.CharField(
        verbose_name="How was this confirmed?",
        max_length=50,
        choices=CONTACT,
    )

    confirmed_by_other = OtherCharField()

    comment = models.TextField(
        verbose_name="Comment",
        null=True,
        blank=True,
        help_text="Provide any additional details, if relevant",
    )

    class Meta:
        abstract = True
