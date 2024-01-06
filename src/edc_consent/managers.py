from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from .stubs import ConsentLikeModel


class ObjectConsentManager(models.Manager):
    def get_by_natural_key(self, subject_identifier_as_pk):
        return self.get(subject_identifier_as_pk=subject_identifier_as_pk)


class ConsentManager(models.Manager):
    def first_consent(self, subject_identifier=None) -> ConsentLikeModel:
        """Returns the first consent by consent_datetime."""
        return (
            self.filter(subject_identifier=subject_identifier)
            .order_by("consent_datetime")
            .first()
        )
