from django.db import models

from ..models import CurrentSiteManager, SiteModelMixin


class TestModelWithSite(SiteModelMixin, models.Model):
    f1 = models.CharField(max_length=10, default="1")

    objects = models.Manager()

    on_site = CurrentSiteManager()
