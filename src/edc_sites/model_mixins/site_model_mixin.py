from __future__ import annotations

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction

from ..managers import CurrentSiteManager
from ..site import sites
from ..utils import get_site_model_cls


class SiteModelMixinError(Exception):
    pass


class SiteModelMixin(models.Model):
    site = models.ForeignKey(
        "sites.site",
        on_delete=models.PROTECT,
        null=True,
        related_name="+",
    )

    on_site = CurrentSiteManager()

    def save(self, *args, **kwargs):
        self.update_site_on_save(*args, **kwargs)
        super().save(*args, **kwargs)

    def update_site_on_save(self, *args, **kwargs) -> None:  # noqa: ARG002
        if not self.id:
            if not self.site_id and not self.site:
                self.site = self.get_site_on_create()
        elif "update_fields" in kwargs and "site" not in kwargs.get("update_fields"):
            pass
        else:
            self.validate_site_against_current()

    def get_site_on_create(self) -> Site:
        """Returns a site model instance.

        See also django-multisite.
        """
        try:
            site_obj = self.site
        except ObjectDoesNotExist:
            site_obj = None
        if not site_obj:
            if self.site_id:
                self.site = Site.objects.get(id=self.site_id)
            else:
                try:
                    with transaction.atomic():
                        site_obj = get_site_model_cls().objects.get_current()
                except ObjectDoesNotExist as e:
                    site_ids = [str(s) for s in sites.all()]
                    raise SiteModelMixinError(
                        "Exception raised when trying manager method `get_current()`. "
                        f"Sites registered with `sites` global are {site_ids}. "
                        f"settings.SITE_ID={settings.SITE_ID}. Got {e}."
                    ) from e
        return site_obj

    def validate_site_against_current(self) -> None:
        """Validate existing site instance matches current_site."""
        return

    class Meta:
        abstract = True
