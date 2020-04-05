import re

from django.db import models
from edc_constants.constants import UUID_PATTERN
from edc_identifier import is_subject_identifier_or_raise
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_search.model_mixins import SearchSlugModelMixin

from ..screening_identifier import ScreeningIdentifier


class ScreeningIdentifierModelMixin(
    NonUniqueSubjectIdentifierModelMixin, SearchSlugModelMixin, models.Model
):

    identifier_cls = ScreeningIdentifier
    screening_identifier_field_name = "screening_identifier"

    def save(self, *args, **kwargs):
        """Screening Identifier is always allocated.
        """
        if not self.id:
            setattr(
                self,
                self.screening_identifier_field_name,
                self.identifier_cls().identifier,
            )
        super().save(*args, **kwargs)

    def update_subject_identifier_on_save(self):
        """Overridden to not create a new study-allocated subject identifier on save.

        Instead just set subject_identifier to a UUID for uniqueness
        from subject_identifier_as_pk.

        The subject_identifier will be set upon consent.
        """
        if not self.subject_identifier:
            self.subject_identifier = self.subject_identifier_as_pk.hex
        else:
            # validate it is either a valid subject identifier or a
            # uuid/uuid.hex
            if not re.match(UUID_PATTERN, self.subject_identifier):
                is_subject_identifier_or_raise(
                    self.subject_identifier, reference_obj=self
                )
        return self.subject_identifier

    def make_new_identifier(self):
        return self.subject_identifier_as_pk.hex

    class Meta:
        abstract = True
