from django.db import models
from django.db.models.deletion import PROTECT
from edc_model import models as edc_models
from edc_model.models import datetime_not_future
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils import get_utcnow

from .aliquot import Aliquot


class OrderManager(models.Manager):
    def get_by_natural_key(self, report_datetime, aliquot_identifier):
        return self.get(
            report_datetime=report_datetime,
            aliquot__aliquot_identifier=aliquot_identifier,
        )


class Order(SiteModelMixin, edc_models.BaseUuidModel):

    aliquot = models.ForeignKey(Aliquot, on_delete=PROTECT)

    order_identifier = models.CharField(max_length=25, editable=False, unique=True)

    order_datetime = models.DateTimeField(
        default=get_utcnow, validators=[datetime_not_future]
    )

    panel_name = models.CharField(max_length=25)

    on_site = CurrentSiteManager()

    objects = OrderManager()

    history = edc_models.HistoricalRecords()

    def natural_key(self):
        return (self.report_datetime,) + self.aliquot.natural_key()

    natural_key.dependencies = ["edc_lab.aliquot", "sites.Site"]

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Order"
