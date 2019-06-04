from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import PROTECT
from edc_action_item.models.action_model_mixin import ActionModelMixin
from edc_constants.constants import NEW, CLOSED, OPEN, FEEDBACK, RESOLVED
from edc_model.models import BaseUuidModel
from edc_registration.models import RegisteredSubject
from edc_utils.date import get_utcnow

from ..action_items import DATA_QUERY_ACTION
from edc_auth import slugify_user

User = get_user_model()


STATUS = (
    (NEW, "New"),
    (OPEN, "Open"),
    (FEEDBACK, "Feedback"),
    (RESOLVED, "Resolved"),
    (CLOSED, "Closed"),
)


class DataManagerQuery(ActionModelMixin, BaseUuidModel):

    tracking_identifier_prefix = "DQ"

    action_name = DATA_QUERY_ACTION

    report_datetime = models.DateTimeField(default=get_utcnow)

    sender = models.ForeignKey(User, related_name="sender", on_delete=PROTECT)

    recipients = models.ManyToManyField(User, related_name="recipients")

    recipients_as_list = models.TextField(editable=False)

    registered_subject = models.ForeignKey(
        RegisteredSubject, verbose_name="Subject Identifier", on_delete=PROTECT
    )

    title = models.CharField(max_length=35)

    status = models.CharField(max_length=25, choices=STATUS, default=NEW)

    comment = models.TextField(
        verbose_name="Data manager's comment", null=True, blank=True
    )

    response = models.TextField(
        verbose_name="Clinic / Field comment", null=True, blank=True
    )

    def __str__(self):
        return (
            f"{self.subject_identifier}: {self.title} [{self.action_identifier[-9:]}]"
        )

    def save(self, *args, **kwargs):
        self.recipients_as_list = ",".join(
            [f"{slugify_user(o)}" for o in self.recipients.all()]
        )
        super().save(*args, **kwargs)

    @property
    def subject_identifier(self):
        return self.registered_subject.subject_identifier
