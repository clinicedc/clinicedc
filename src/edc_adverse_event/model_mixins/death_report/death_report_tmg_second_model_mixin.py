from django.db import models

from edc_action_item.managers import (
    ActionIdentifierModelManager,
    ActionIdentifierSiteManager,
)

from ...constants import DEATH_REPORT_TMG_SECOND_ACTION


class DeathReportTmgSecondManager(ActionIdentifierModelManager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(action_item__action_type__name=DEATH_REPORT_TMG_SECOND_ACTION)


class DeathReportTmgSecondSiteManager(ActionIdentifierSiteManager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(action_item__action_type__name=DEATH_REPORT_TMG_SECOND_ACTION)


class DeathReportTmgSecondModelMixin(models.Model):
    action_name = DEATH_REPORT_TMG_SECOND_ACTION

    objects = DeathReportTmgSecondManager()

    on_site = DeathReportTmgSecondSiteManager()

    class Meta:
        abstract = True
        verbose_name = "Death Report TMG (2nd)"
        verbose_name_plural = "Death Report TMG (2nd)"
