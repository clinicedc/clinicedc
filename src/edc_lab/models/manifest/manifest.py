from django.db import models
from django.db.models.deletion import PROTECT

from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_pdf_reports.model_mixins import PdfReportModelMixin
from edc_search.model_mixins import SearchSlugManager, SearchSlugModelMixin
from edc_sites.managers import CurrentSiteManager

from ...managers import ManifestManager
from ...model_mixins import ManifestModelMixin
from ...pdf_reports import ManifestPdfReport
from .consignee import Consignee
from .shipper import Shipper


class Manager(ManifestManager, SearchSlugManager):
    pass


class Manifest(ManifestModelMixin, PdfReportModelMixin, SearchSlugModelMixin, BaseUuidModel):
    pdf_report_cls = ManifestPdfReport

    def get_search_slug_fields(self):
        return (
            "manifest_identifier",
            "human_readable_identifier",
            "shipper.name",
            "consignee.name",
        )

    consignee = models.ForeignKey(Consignee, verbose_name="Consignee", on_delete=PROTECT)

    shipper = models.ForeignKey(Shipper, verbose_name="Shipper/Exporter", on_delete=PROTECT)

    objects = Manager()

    on_site = CurrentSiteManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.manifest_identifier,)

    natural_key.dependencies = ("edc_lab.shipper", "edc_lab.consignee")

    def __str__(self):
        return "{} created on {} by {}".format(
            self.manifest_identifier,
            self.manifest_datetime.strftime("%Y-%m-%d"),
            self.user_created,
        )

    @property
    def count(self):
        return self.manifestitem_set.all().count()

    class Meta(ManifestModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = "Manifest"
