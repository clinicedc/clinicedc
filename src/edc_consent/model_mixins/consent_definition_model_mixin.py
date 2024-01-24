from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ImproperlyConfigured
from django.db import models

from edc_consent.site_consents import site_consents

if TYPE_CHECKING:
    from edc_consent.consent_definition import ConsentDefinition


class ConsentDefinitionModelMixin(models.Model):
    consent_definition: ConsentDefinition = None

    def save(self, *args, **kwargs):
        self.get_consent_definition()
        super().save(*args, **kwargs)

    def get_consent_definition(self) -> ConsentDefinition:
        """Verify the consent definition is registered with
        site_consent.
        """
        if self.consent_definition is None:
            raise ImproperlyConfigured(
                f"ConsentDefinition is required for screening model. See {self.__class__}."
            )
        else:
            consent_definition = site_consents.get(self.consent_definition.name)
        return consent_definition

    class Meta:
        abstract = True
