from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import PROTECT
from edc_action_item.models.action_model_mixin import ActionModelMixin
from edc_constants.constants import OPEN, FEEDBACK, RESOLVED, NEW, NOT_APPLICABLE
from edc_constants.choices import YES_NO_NA
from edc_model.models import BaseUuidModel
from edc_utils.date import get_utcnow
from edc_registration.models import RegisteredSubject

from ..action_items import DATA_QUERY_ACTION
from .data_dictionary import DataDictionary
from .visit_schedule import VisitSchedule

User = get_user_model()

RESPONSE_STATUS = (
    (NEW, "New"),
    (OPEN, "Open"),
    (FEEDBACK, "Feedback"),
    (RESOLVED, "Resolved")
)


class DataManagerQuery(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = "DQ"

    action_name = DATA_QUERY_ACTION

    report_datetime = models.DateTimeField(
        verbose_name="Query date",
        default=get_utcnow,
    )

    subject_identifier = models.CharField(
        max_length=50, null=True, editable=False)

    sender = models.ForeignKey(
        User,
        related_name="sender",
        on_delete=PROTECT,
        verbose_name="Query raised by",
        help_text="select a name from the list",
    )

    recipient = models.ForeignKey(
        User,
        related_name="recipient",
        on_delete=PROTECT,
        verbose_name="Sent to",
        help_text="select a name from the list",
    )

    registered_subject = models.ForeignKey(
        RegisteredSubject,
        verbose_name="Subject Identifier",
        on_delete=PROTECT,
        null=True,
        blank=False,
    )

    visit_schedule = models.ForeignKey(
        VisitSchedule,
        verbose_name="Visit",
        on_delete=PROTECT,
        null=True,
        blank=True,
        help_text="select all that apply",
    )

    data_dictionaries = models.ManyToManyField(
        DataDictionary,
        verbose_name="Question(s)",
        blank=True,
        help_text="select all that apply",
    )

    query_text = models.TextField(help_text="Describe the query in detail.")

    response_datetime = models.DateTimeField(
        verbose_name="Date",
        null=True, blank=True,
    )

    response_text = models.TextField(null=True, blank=True)

    response_status = models.CharField(
        max_length=25, choices=RESPONSE_STATUS, default=NEW
    )

    resolved = models.CharField(
        max_length=25,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
    )

    resolved_user = models.ForeignKey(
        User,
        verbose_name="Resolved by",
        related_name="resolved_user",
        on_delete=PROTECT,
        null=True, blank=True,
        help_text="select a name from the list",
    )

    resolved_datetime = models.DateTimeField(
        verbose_name="Resolved on", null=True, blank=True
    )

    plan_of_action = models.TextField(
        null=True, blank=True,
        help_text="If required, provide a plan of action",
    )

    def __str__(self):
        return f"{self.action_identifier[-9:]}"

    def save(self, *args, **kwargs):
        self.subject_identifier = self.registered_subject.subject_identifier
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Data Query"
        verbose_name_plural = "Data Queries"
