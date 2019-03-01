from django.contrib.sites.models import Site
from django.db import models

from .utils import raise_on_save_if_reviewer


class SiteModelError(Exception):
    pass


class SiteModelMixin(models.Model):

    site = models.ForeignKey(Site, on_delete=models.PROTECT, null=True, editable=False)

    def save(self, *args, **kwargs):
        raise_on_save_if_reviewer()
        if not self.site:
            self.site = Site.objects.get_current()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
