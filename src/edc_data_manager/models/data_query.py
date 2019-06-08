from django.db import models
from django.db.models.deletion import PROTECT
from edc_action_item.models.action_model_mixin import ActionModelMixin
from edc_constants.constants import OPEN, FEEDBACK, RESOLVED, NEW
from edc_model.models import BaseUuidModel
from edc_utils.date import get_utcnow

from ..action_items import DATA_QUERY_ACTION
from ..constants import RESOLVED_WITH_ACTION
from .data_dictionary import DataDictionary
from .query_subject import QuerySubject
from .query_visit_schedule import QueryVisitSchedule
from .user import QueryUser, DataManagerUser


RESPONSE_STATUS = (
    (NEW, "New"),
    (OPEN, "Open"),
    (FEEDBACK, "Feedback"),
    (RESOLVED, "Resolved"),
)


TCC_STATUS = (
    (OPEN, "Open"),
    (RESOLVED, "Resolved"),
    (RESOLVED_WITH_ACTION, "Resolved, with plan of action"),
)


class DataQuery(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = "DQ"

    action_name = DATA_QUERY_ACTION

    report_datetime = models.DateTimeField(
        verbose_name="Query date",
        default=get_utcnow,
    )

    subject_identifier = models.CharField(
        max_length=50, null=True, editable=False)

    sender = models.ForeignKey(
        DataManagerUser,
        related_name="sender",
        on_delete=PROTECT,
        verbose_name="Query raised by",
        help_text="select a name from the list",
    )

    recipient = models.ForeignKey(
        QueryUser,
        related_name="recipient",
        on_delete=PROTECT,
        verbose_name="Sent to",
        help_text="select a name from the list",
    )

    registered_subject = models.ForeignKey(
        QuerySubject,
        verbose_name="Subject Identifier",
        on_delete=PROTECT,
        null=True,
        blank=False,
    )

    visit_schedule = models.ForeignKey(
        QueryVisitSchedule,
        verbose_name="Visit",
        on_delete=PROTECT,
        null=True,
        blank=True,
        help_text="select all that apply",
    )

    visit_code_sequence = models.IntegerField(
        verbose_name="Visit code sequence",
        default=0,
        help_text=(
            "Defaults to '0'. For example, when combined with the "
            "visit code `1000` would make `1000.0`.")
    )

    timepoint = models.DecimalField(
        null=True, decimal_places=1, max_digits=6,
    )

    data_dictionaries = models.ManyToManyField(
        DataDictionary,
        verbose_name="Question(s)",
        blank=True,
        help_text="select all that apply",
    )

    query_text = models.TextField(help_text="Describe the query in detail.")

    site_resolved_datetime = models.DateTimeField(
        verbose_name="Site resolved on",
        null=True, blank=True,
    )

    site_response_text = models.TextField(
        null=True, blank=True,
    )

    site_response_status = models.CharField(
        verbose_name="Site status",
        max_length=25, choices=RESPONSE_STATUS, default=NEW
    )

    status = models.CharField(
        verbose_name="TCC status",
        max_length=25,
        choices=TCC_STATUS,
        default=OPEN,
    )

    resolved_user = models.ForeignKey(
        DataManagerUser,
        verbose_name="TCC resolved by",
        related_name="resolved_user",
        on_delete=PROTECT,
        null=True, blank=True,
        help_text="select a name from the list",
    )

    resolved_datetime = models.DateTimeField(
        verbose_name="TCC resolved on", null=True, blank=True
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
