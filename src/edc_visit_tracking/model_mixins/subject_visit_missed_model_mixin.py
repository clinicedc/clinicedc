from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from edc_constants.choices import ALIVE_DEAD_UNKNOWN, YES_NO, YES_NO_NA
from edc_constants.constants import NO, NOT_APPLICABLE
from edc_model import models as edc_models
from edc_model.validators import date_not_future
from edc_protocol.validators import date_not_before_study_start

from ..constants import VISIT_MISSED_ACTION


class SubjectVisitMissedModelMixin(models.Model):
    """Declare with:

        missed_reasons = models.ManyToManyField(SubjectVisitMissedReasons, blank=True)

    And include in your `lists` app:

        class SubjectVisitMissed(
            CrfModelMixin,
            SubjectVisitMissedModelMixin,
            edc_models.BaseUuidModel):

            subject_visit = models.OneToOneField(
                settings.SUBJECT_VISIT_MODEL,
                on_delete=models.PROTECT,
            )

            missed_reasons = models.ManyToManyField(
                SubjectVisitMissedReasons, blank=True
            )

            class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
                verbose_name = "Missed Visit Report"
                verbose_name_plural = "Missed Visit Report"
    """

    action_name = VISIT_MISSED_ACTION

    survival_status = models.CharField(
        verbose_name=_("Survival status"),
        max_length=25,
        choices=ALIVE_DEAD_UNKNOWN,
        help_text=_("If deceased, complete the death report"),
    )

    contact_attempted = models.CharField(
        verbose_name=_(
            "Were any attempts made to contact the participant "
            "since the expected appointment date?"
        ),
        max_length=25,
        choices=YES_NO,
        help_text=_("Not including pre-appointment reminders"),
    )

    contact_attempts_count = models.IntegerField(
        verbose_name=_(
            "Number of attempts made to contact participantsince the expected appointment date"
        ),
        validators=[MinValueValidator(1)],
        help_text=_(
            "Not including pre-appointment reminders. Multiple attempts "
            "on the same day count as a single attempt."
        ),
        null=True,
        blank=True,
    )

    contact_attempts_explained = models.TextField(
        verbose_name=_("If contact not made and less than 3 attempts, please explain"),
        default="",
        blank=True,
    )

    contact_last_date = models.DateField(
        verbose_name=_("Date of last telephone contact/attempt"),
        validators=[date_not_future, date_not_before_study_start],
        null=True,
        blank=True,
    )

    contact_made = models.CharField(
        verbose_name=_("Was contact finally made with the participant?"),
        max_length=25,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
    )

    missed_reasons = models.ManyToManyField(
        "edc_visit_tracking.SubjectVisitMissedReasons", blank=True
    )

    missed_reasons_other = edc_models.OtherCharField()

    ltfu = models.CharField(
        verbose_name=_("Has the participant met the protocol criteria for lost to follow up?"),
        max_length=15,
        choices=YES_NO_NA,
        default=NO,
        help_text=_("If 'Yes', complete the Loss to Follow up form"),
    )

    comment = models.TextField(
        verbose_name=_("Please provide further details, if any"),
        default="",
        blank=True,
    )

    class Meta:
        abstract = True
        indexes = (models.Index(fields=["action_identifier", "site", "id"]),)
