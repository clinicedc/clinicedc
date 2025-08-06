from django.db import models

from edc_sites.managers import CurrentSiteManager
from edc_sites.model_mixins import SiteModelMixin


class TestModelWithSite(SiteModelMixin, models.Model):
    f1 = models.CharField(max_length=10, default="1")

    objects = models.Manager()

    on_site = CurrentSiteManager()

    class Meta:
        verbose_name = "Test Model"
