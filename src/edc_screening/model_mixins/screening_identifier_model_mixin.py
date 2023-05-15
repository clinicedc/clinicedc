from django.db import models
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_search.model_mixins import SearchSlugModelMixin

from ..screening_identifier import ScreeningIdentifier
from ..stubs import SubjectScreeningModelStub


class ScreeningIdentifierModelMixin(
    NonUniqueSubjectIdentifierModelMixin, SearchSlugModelMixin, models.Model
):
    identifier_cls = ScreeningIdentifier
    screening_identifier_field_name: str = "screening_identifier"

    def save(self, *args, **kwargs):
        """Screening Identifier is always allocated."""
        if not self.id:
            setattr(
                self,
                self.screening_identifier_field_name,
                self.identifier_cls().identifier,
            )
        super().save(*args, **kwargs)  # type:ignore

    def update_subject_identifier_on_save(self: SubjectScreeningModelStub) -> str:
        """Overridden to not create a new study-allocated subject
        identifier on save.

        Only gets called if self.id is None (create).

        Instead, just copy subject_identifier_as_pk to
        subject_identifier to maintain uniqueness.

        The "real" subject_identifier will be set upon consent.

        See SubjectIdentifierMethodsModelMixin. \
            update_subject_identifier_on_save()
        """
        if not self.subject_identifier:
            self.subject_identifier = self.make_new_identifier()
        return self.subject_identifier

    def make_new_identifier(self) -> str:
        return self.subject_identifier_as_pk.hex

    class Meta:
        abstract = True
