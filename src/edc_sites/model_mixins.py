from __future__ import annotations

from django.contrib.sites.managers import CurrentSiteManager as BaseCurrentSiteManager
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction


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
                    site = Site.objects.get_current()
            except ObjectDoesNotExist as e:
                raise SiteModelMixinError(e)
        return site or self.site

    def validate_site_against_current(self) -> None:
        """Validate existing site instance matches current_site."""
        pass

    class Meta:
        abstract = True
