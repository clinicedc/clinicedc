from django.db import models
from edc_action_item.models.action_model_mixin import ActionModelMixin
from edc_constants.choices import YES_NO_TBD
from edc_constants.constants import TBD
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models.base_uuid_model import BaseUuidModel
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils.date import get_utcnow

from ..constants import UNBLINDING_REVIEW_ACTION
from .unblinding_user import UnblindingReviewerUser


class UnblindingReview(
    NonUniqueSubjectIdentifierFieldMixin,
    SiteModelMixin,
    ActionModelMixin,
    BaseUuidModel,
):
    action_name = UNBLINDING_REVIEW_ACTION

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time", default=get_utcnow
    )

    reviewer = models.ForeignKey(
        UnblindingReviewerUser,
        related_name="+",
        on_delete=models.PROTECT,
        verbose_name="Unblinding request reviewed by",
        help_text="Choose a name from the list",
    )

    approved = models.CharField(max_length=15, default=TBD, choices=YES_NO_TBD)

    comment = models.TextField(verbose_name="Comment", null=True)

    objects = SubjectIdentifierManager()

    on_site = CurrentSiteManager()

    def natural_key(self):
        return (self.action_identifier,)

    class Meta:
        verbose_name = "Unblinding Review"
        verbose_name_plural = "Unblinding Reviews"
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
