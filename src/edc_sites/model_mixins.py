from __future__ import annotations

from django.contrib.sites.managers import CurrentSiteManager as BaseCurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models


class SiteModelMixinError(Exception):
    pass


class CurrentSiteManager(BaseCurrentSiteManager):
    use_in_migrations = True

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class SiteModelMixin(models.Model):
    site = models.ForeignKey(
        Site, on_delete=models.PROTECT, null=True, editable=False, related_name="+"
    )

    on_site = CurrentSiteManager()

    def save(self, *args, **kwargs):
        if not self.id:
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
        current_site = Site.objects.get_current()
        return current_site if not self.site else self.site

    def validate_site_against_current(self) -> None:
        """Validate existing site instance matches current_site."""
        pass
        # current_site = Site.objects.get_current()
        # if self.site != current_site:
        #     site = current_site
        #     raise SiteModelMixinError(
        #         f"Invalid attempt to change site! Expected `{self.site}`. "
        #         f"Tried to change to `{current_site}`. Model=`{self}`. id=`{self.id}`."
        #     )

    class Meta:
        abstract = True
