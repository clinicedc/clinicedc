from django.db import models
from edc_action_item.managers import (
    ActionIdentifierSiteManager,
    ActionIdentifierManager,
)
from edc_action_item.models import ActionModelMixin
from edc_constants.choices import YES_NO
from edc_constants.constants import YES, NOT_APPLICABLE
from edc_identifier.model_mixins import TrackingModelMixin
from edc_model.validators import date_not_future
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow

from ..constants import AE_FOLLOWUP_ACTION
from ..choices import AE_OUTCOME, AE_GRADE_SIMPLE


class AeFollowupModelMixin(ActionModelMixin, TrackingModelMixin, SiteModelMixin):

    """Declaration, for example:

    from django.db.models.deletion import PROTECT

    from .ae_initial import AeInitial

    class AeFollowupModel(AeFollowupModelMixin, BaseUuidModel):

        ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    """

    action_name = AE_FOLLOWUP_ACTION

    tracking_identifier_prefix = "AF"

    # ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date and time", default=get_utcnow
    )

    outcome = models.CharField(
        blank=False, null=False, max_length=25, choices=AE_OUTCOME
    )

    outcome_date = models.DateField(validators=[date_not_future])

    ae_grade = models.CharField(
        verbose_name="If severity increased, indicate grade",
        max_length=25,
        choices=AE_GRADE_SIMPLE,
        default=NOT_APPLICABLE,
    )

    relevant_history = models.TextField(
        verbose_name="Description summary of Adverse Event outcome",
        max_length=1000,
        blank=False,
        null=False,
        help_text="Indicate Adverse Event, clinical results,"
        "medications given, dosage,treatment plan and outcomes.",
    )

    followup = models.CharField(
        verbose_name="Is a follow-up to this report required?",
        max_length=15,
        choices=YES_NO,
        default=YES,
        help_text="If NO, this will be considered the final report",
    )

    on_site = ActionIdentifierSiteManager()

    objects = ActionIdentifierManager()

    def __str__(self):
        return f"{self.action_identifier[-9:]}"

    def save(self, *args, **kwargs):
        self.subject_identifier = self.ae_initial.subject_identifier
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.action_identifier,)

    @property
    def report_date(self):
        """Returns a date based on the UTC datetime.
        """
        return self.report_datetime.date()

    @property
    def severity(self):
        if self.ae_grade == NOT_APPLICABLE:
            return "unchanged"
        return self.ae_grade

    def get_action_item_reason(self):
        return self.ae_initial.ae_description

    class Meta:
        abstract = True
        verbose_name = "AE Follow-up Report"
        indexes = [
            models.Index(
                fields=["subject_identifier", "action_identifier", "site", "id"]
            )
        ]
