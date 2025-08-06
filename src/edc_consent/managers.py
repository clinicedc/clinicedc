from __future__ import annotations

from django.db import models

from edc_search.model_mixins import SearchSlugManager
from edc_sites.managers import CurrentSiteManager

from .site_consents import site_consents


class ConsentObjectsManager(SearchSlugManager, models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, subject_identifier_as_pk):
        return self.get(subject_identifier_as_pk=subject_identifier_as_pk)


class ConsentObjectsByCdefManager(ConsentObjectsManager):
    """An objects model manager to use on consent proxy models
    linked to a ConsentDefinition.

    Filters queryset by the proxy model's label_lower
    """

    def get_queryset(self):
        qs = super().get_queryset()
        cdef = site_consents.get_consent_definition(model=qs.model._meta.label_lower)
        return qs.filter(version=cdef.version)


class CurrentSiteByCdefManager(CurrentSiteManager):
    """A site model manager to use on consent proxy models
    linked to a ConsentDefinition.

    Filters queryset by the proxy model's label_lower
    """

    def get_queryset(self):
        qs = super().get_queryset()
        cdef = site_consents.get_consent_definition(model=qs.model._meta.label_lower)
        return qs.filter(site_id=cdef.site.site_id, version=cdef.version)
