from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_mixins import BaseUuidModel
from edc_base.model_managers import HistoricalRecords
from edc_base.sites import CurrentSiteManager

from .model_mixins import ResultModelMixin
from .order import Order


class ResultManager(models.Manager):

    def get_by_natural_key(self, report_datetime, order_identifier):
        return self.get(
            report_datetime=report_datetime,
            order__order_identifier=order_identifier)


class Result(ResultModelMixin, BaseUuidModel):

    order = models.ForeignKey(Order, on_delete=PROTECT)

    on_site = CurrentSiteManager()

    objects = ResultManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.report_datetime, self.order.order_identifier,)
    natural_key.dependencies = ['edc_lab.order', 'edc_lab.panel', 'sites.Site']
