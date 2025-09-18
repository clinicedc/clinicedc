from django.db import models
from django.db.models.deletion import PROTECT

from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.managers import CurrentSiteManager

from ..model_mixins import ResultItemModelMixin
from .result import Result


class ResultItemManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, report_datetime, requisition_identifier):
        return self.get(
            report_datetime=report_datetime,
            requisition__requisition_identifier=requisition_identifier,
        )


class ResultItem(ResultItemModelMixin, BaseUuidModel):
    result = models.ForeignKey(Result, on_delete=PROTECT)

    objects = ResultItemManager()

    on_site = CurrentSiteManager()

    history = HistoricalRecords()

    def natural_key(self):
        return self.report_datetime, *self.result.natural_key()

    natural_key.dependencies = ("edc_lab.result", "sites.Site")

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Result Item"
