from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from django.db import models

from ...visit_sequence import VisitSequence, VisitSequenceError

if TYPE_CHECKING:
    from edc_appointment.models import Appointment
    from edc_visit_tracking.typing_stubs import RelatedVisitProtocol


class PreviousVisitError(Exception):
    pass


class PreviousVisitModelMixin(models.Model):
    """A model mixin to force the user to complete visit model
    instances in sequence.

    * Ensures the previous visit exists before allowing save()
      by raising PreviousVisitError.
    * If the visit is the first in the sequence, save() is allowed.
    """

    visit_sequence_cls: type[VisitSequence] = VisitSequence

    def save(self, *args, **kwargs) -> None:
        self.validate_visit_sequence()
        super().save(*args, **kwargs)

    def validate_visit_sequence(
        self: Appointment | RelatedVisitProtocol | Self,
    ) -> None:
        try:
            appointment = self.related_visit.appointment
        except AttributeError as e:
            if "related_visit" not in str(e):
                raise
            appointment = self.appointment
        visit_sequence = self.visit_sequence_cls(appointment=appointment)
        try:
            visit_sequence.enforce_sequence()
        except VisitSequenceError as e:
            raise PreviousVisitError(e) from e

    @property
    def previous_visit(self: Appointment | RelatedVisitProtocol | Self) -> Any:
        try:
            appointment = self.related_visit.appointment
        except AttributeError as e:
            if "related_visit" not in str(e):
                raise
            appointment = self.appointment
        visit_sequence = self.visit_sequence_cls(appointment=appointment)
        return visit_sequence.previous_visit

    class Meta:
        abstract = True
