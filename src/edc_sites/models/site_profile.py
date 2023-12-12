from __future__ import annotations

import json

from django.contrib.sites.models import Site
from django.db import models


class SiteProfile(models.Model):
    id = models.BigAutoField(primary_key=True)

    country = models.CharField(max_length=250, null=True)

    country_code = models.CharField(max_length=15, null=True)

    languages = models.TextField(null=True)

    title = models.CharField(max_length=250, null=True)

    site = models.OneToOneField(Site, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.site.id}: {self.title}"

    def get_languages(self):
        return json.loads(self.languages)
