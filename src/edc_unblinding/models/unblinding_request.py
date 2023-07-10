from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
)
from django.db import models
from edc_action_item.models.action_model_mixin import ActionModelMixin
from edc_constants.choices import YES_NO_TBD
from edc_constants.constants import TBD
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models.base_uuid_model import BaseUuidModel
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils.date import get_utcnow

from ..constants import UNBLINDING_REQUEST_ACTION
from .unblinding_user import UnblindingRequestorUser


class UnblindingRequest(
    NonUniqueSubjectIdentifierFieldMixin,
    SiteModelMixin,
    ActionModelMixin,
    BaseUuidModel,
):
    action_name = UNBLINDING_REQUEST_ACTION

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time", default=get_utcnow
    )

    initials = models.CharField(
        verbose_name="Subject's initials",
        max_length=3,
        validators=[
            RegexValidator("[A-Z]{1,3}", "Invalid format"),
            MinLengthValidator(2),
            MaxLengthValidator(3),
        ],
        help_text="Use UPPERCASE letters only. May be 2 or 3 letters.",
    )

    requestor = models.ForeignKey(
        UnblindingRequestorUser,
        related_name="+",
        on_delete=models.PROTECT,
        verbose_name="Unblinding requested by",
        help_text="Choose a name from the list",
    )

    unblinding_reason = models.TextField(verbose_name="Reason for unblinding")

    approved = models.CharField(max_length=15, default=TBD, choices=YES_NO_TBD)

    approved_datetime = models.DateTimeField(null=True)

    objects = SubjectIdentifierManager()

    on_site = CurrentSiteManager()

    def natural_key(self):
        return (self.action_identifier,)

    class Meta:
        verbose_name = "Unblinding Request"
        verbose_name_plural = "Unblinding Requests"
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
