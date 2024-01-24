from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ImproperlyConfigured
from django.db import models

from edc_consent import site_consents

if TYPE_CHECKING:
    from edc_consent.consent_definition import ConsentDefinition


class ConsentDefinitionModelMixin(models.Model):
    consent_definition: ConsentDefinition = None

    def save(self, *args, **kwargs):
        if self.consent_definition is None:
            raise ImproperlyConfigured(
                f"ConsentDefinition is required for screening model. See {self.__class__}."
            )
        else:
            # verify the consent definition is registered with
            # site_consents
            site_consents.get(self.consent_definition.name)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
