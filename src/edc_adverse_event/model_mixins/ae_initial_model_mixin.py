from django.apps import apps as django_apps
from django.db import models
from edc_action_item.managers import (
    ActionIdentifierSiteManager,
    ActionIdentifierManager,
)
from edc_action_item.models import ActionModelMixin
from edc_constants.choices import YES_NO, YES_NO_UNKNOWN
from edc_identifier.model_mixins import TrackingModelMixin
from edc_model_fields.fields import OtherCharField
from edc_sites.models import SiteModelMixin

from ..constants import AE_INITIAL_ACTION
from ..choices import AE_CLASSIFICATION
from .ae_model_mixin import AeModelMixin


class AeInitialModelMixin(
    AeModelMixin, ActionModelMixin, TrackingModelMixin, SiteModelMixin, models.Model
):

    """
    Declaration, for example:

    from edc_model.models import BaseUuidModel
    from edc_adverse_event.model_mixins AeInitialModelMixin


    class AeInitial(AeInitialModelMixin, BaseUuidModel):
        pass
    """

    tracking_identifier_prefix = "AE"

    action_name = AE_INITIAL_ACTION

    ae_followup_model_name = "ambition_ae.aefollowup"

    ae_classification = models.CharField(choices=AE_CLASSIFICATION, max_length=150)

    #     ae_classification = models.ForeignKey(
    #         "edc_adverse_event.AeClassification", on_delete=PROTECT,
    #         null=True,
    #     )

    ae_classification_other = OtherCharField(max_length=250, blank=True, null=True)

    ae_study_relation_possibility = models.CharField(
        verbose_name=(
            "Is the incident related to the patient involvement in the study?"
        ),
        max_length=10,
        choices=YES_NO_UNKNOWN,
    )

    ae_cause = models.CharField(
        verbose_name=(
            "Has a reason other than the specified study drug been "
            "identified as the cause of the event(s)?"
        ),
        choices=YES_NO,
        max_length=5,
    )

    ae_cause_other = OtherCharField(
        verbose_name='If "Yes", specify', max_length=250, blank=True, null=True
    )

    ae_treatment = models.TextField(
        verbose_name="Specify action taken for treatment of AE:"
    )

    on_site = ActionIdentifierSiteManager()

    objects = ActionIdentifierManager()

    def __str__(self):
        return f"{self.action_identifier[-9:]} Grade {self.ae_grade}"

    def natural_key(self):
        return (self.action_identifier,)

    def get_action_item_reason(self):
        return self.ae_description

    @property
    def ae_follow_ups(self):
        AeFollowup = django_apps.get_model(self.ae_followup_model_name)
        return AeFollowup.objects.filter(ae_initial=self).order_by("report_datetime")

    @property
    def description(self):
        """Returns a description.
        """
        return f"{self.action_identifier[-9:]} Grade-{self.ae_grade}. {self.ae_description}"

    class Meta:
        abstract = True
        verbose_name = "AE Initial Report"
        indexes = [
            models.Index(
                fields=["subject_identifier", "action_identifier", "site", "id"]
            )
        ]
