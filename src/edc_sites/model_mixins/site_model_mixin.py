from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction

from ..managers import CurrentSiteManager
from ..site import sites
from ..utils import get_site_model_cls

if TYPE_CHECKING:
    from django.contrib.sites.models import Site


class SiteModelMixinError(Exception):
    pass


class SiteModelMixin(models.Model):
    site = models.ForeignKey(
        "sites.site",
        on_delete=models.PROTECT,
        null=True,
        # editable=False,
        related_name="+",
    )

    on_site = CurrentSiteManager()

    def save(self, *args, **kwargs):
        if not self.id and not self.site:
            self.site = self.get_site_on_create()
        elif "update_fields" in kwargs and "site" not in kwargs.get("update_fields"):
            pass
        else:
            self.validate_site_against_current()
        super().save(*args, **kwargs)

    def get_site_on_create(self) -> Site:
        """Returns a site model instance.

        See also django-multisite.
        """
        site = None
        if not self.site:
            try:
                with transaction.atomic():
                    site = get_site_model_cls().objects.get_current()
            except ObjectDoesNotExist as e:
                site_ids = [str(s) for s in sites.all()]
                raise SiteModelMixinError(
                    "Exception raised when trying manager method `get_current()`. "
                    f"Sites registered with `sites` global are {site_ids}. "
                    f"settings.SITE_ID={settings.SITE_ID}. Got {e}."
                )
        return site or self.site

    def validate_site_against_current(self) -> None:
        """Validate existing site instance matches current_site."""
        pass

    class Meta:
        abstract = True
