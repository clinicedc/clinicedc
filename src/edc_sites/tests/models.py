from django.db import models

from ..models import SiteModelMixin, CurrentSiteManager


class TestModelWithSite(SiteModelMixin, models.Model):

    f1 = models.CharField(max_length=10, default="1")

    on_site = CurrentSiteManager()

    objects = models.Manager()
