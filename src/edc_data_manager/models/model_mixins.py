from django.db import models
from django.db.models import PROTECT
from edc_constants.constants import CLOSED, NEW, NORMAL, OPEN, RESOLVED
from edc_utils import get_utcnow

from ..choices import DM_STATUS, QUERY_PRIORITY, RESPONSE_STATUS
from ..constants import CLOSED_WITH_ACTION
from .user import DataManagerUser, QueryUser


class DataQueryModelMixin(models.Model):
    report_datetime = models.DateTimeField(verbose_name="Query date", default=get_utcnow)

    title = models.CharField(max_length=150, null=True, blank=False)

    sender = models.ForeignKey(
        DataManagerUser,
        related_name="+",
        on_delete=PROTECT,
        verbose_name="Query raised by",
        help_text="Select a name from the list",
    )

    recipients = models.ManyToManyField(
        QueryUser,
        related_name="+",
        verbose_name="Sent to",
        help_text=(
            "Select any additional recipients. Users in the `Site Data Manager` "
            "group are automatically included."
        ),
        blank=True,
    )

    query_priority = models.CharField(
        verbose_name="Priority", max_length=25, choices=QUERY_PRIORITY, default=NORMAL
    )

    query_text = models.TextField(help_text="Describe the query in detail.")

    site_resolved_datetime = models.DateTimeField(
        verbose_name="Site resolved on", null=True, blank=True
    )

    site_response_text = models.TextField(null=True, blank=True)

    site_response_status = models.CharField(
        verbose_name="Site status", max_length=25, choices=RESPONSE_STATUS, default=NEW
    )

    status = models.CharField(
        verbose_name="DM status", max_length=25, choices=DM_STATUS, default=OPEN
    )

    dm_user = models.ForeignKey(
        DataManagerUser,
        verbose_name="DM resolved by",
        related_name="+",
        on_delete=PROTECT,
        null=True,
        blank=True,
        help_text="select a name from the list",
    )

    resolved_datetime = models.DateTimeField(
        verbose_name="DM resolved on", null=True, blank=True
    )

    auto_resolved = models.BooleanField(default=False)

    plan_of_action = models.TextField(
        null=True, blank=True, help_text="If required, provide a plan of action"
    )

    locked = models.BooleanField(
        default=False,
        help_text="If locked, this query will NEVER be reopened.",
    )

    locked_reason = models.TextField(
        verbose_name="Reason query locked",
        null=True,
        blank=True,
        help_text="If required, the reason the query cannot be resolved.",
    )

    @property
    def dm_resolved(self):
        return self.status in [CLOSED, CLOSED_WITH_ACTION]

    @property
    def site_resolved(self):
        return self.site_response_status == RESOLVED

    class Meta:
        abstract = True
