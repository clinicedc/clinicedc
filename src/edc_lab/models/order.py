from django.db import models
from django.db.models.deletion import PROTECT
from django.utils import timezone

from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_model.validators import datetime_not_future
from edc_sites.managers import CurrentSiteManager
from edc_sites.model_mixins import SiteModelMixin

from .aliquot import Aliquot


class OrderManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, report_datetime, aliquot_identifier):
        return self.get(
            report_datetime=report_datetime,
            aliquot__aliquot_identifier=aliquot_identifier,
        )


class Order(SiteModelMixin, BaseUuidModel):
    aliquot = models.ForeignKey(Aliquot, on_delete=PROTECT)

    order_identifier = models.CharField(max_length=25, editable=False, unique=True)

    order_datetime = models.DateTimeField(
        default=timezone.now, validators=[datetime_not_future]
    )

    panel_name = models.CharField(max_length=25)

    objects = OrderManager()

    on_site = CurrentSiteManager()

    history = HistoricalRecords()

    def natural_key(self):
        return self.report_datetime, *self.aliquot.natural_key()

    natural_key.dependencies = ("edc_lab.aliquot", "sites.Site")

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Order"
