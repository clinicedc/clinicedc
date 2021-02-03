from django.db import models
from edc_action_item.managers import (
    ActionIdentifierManager,
    ActionIdentifierSiteManager,
)

from ..constants import DEATH_REPORT_TMG_SECOND_ACTION
from .death_report_tmg_model_mixin import DeathReportTmgModelMixin


class DeathReportTmgSecondManager(ActionIdentifierManager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(action_item__action_type__name=DEATH_REPORT_TMG_SECOND_ACTION)


class DeathReportTmgSecondSiteManager(ActionIdentifierSiteManager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(action_item__action_type__name=DEATH_REPORT_TMG_SECOND_ACTION)


class DeathReportTmgSecondModelMixin(DeathReportTmgModelMixin):

    action_name = DEATH_REPORT_TMG_SECOND_ACTION

    tracking_identifier_prefix = "DT"

    on_site = DeathReportTmgSecondSiteManager()

    objects = DeathReportTmgSecondManager()

    class Meta:
        abstract = True
        verbose_name = "Death Report TMG (2nd)"
        verbose_name_plural = "Death Report TMG (2nd)"
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
