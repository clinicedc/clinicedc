from typing import Union

from django.db import models
from edc_crf.stubs import CrfModelStub

from ..stubs import SubjectVisitModelStub
from ..visit_sequence import VisitSequence, VisitSequenceError


class PreviousVisitError(Exception):
    pass


class PreviousVisitModelMixin(models.Model):
    """A model mixin to force the user to complete visit model
    instances in sequence.

    * Ensures the previous visit exists before allowing save()
      by raising PreviousVisitError.
    * If the visit is the first in the sequence, save() is allowed.
    """

    visit_sequence_cls = VisitSequence

    def save(
        self: Union[CrfModelStub, SubjectVisitModelStub, "PreviousVisitModelMixin"],
        *args,
        **kwargs
    ):
        try:
            appointment = self.subject_visit.appointment
        except AttributeError:
            appointment = self.appointment
        visit_sequence = self.visit_sequence_cls(appointment=appointment)
        try:
            visit_sequence.enforce_sequence()
        except VisitSequenceError as e:
            raise PreviousVisitError(e)
        super().save(*args, **kwargs)  # type: ignore

    @property
    def previous_visit(
        self: Union[CrfModelStub, SubjectVisitModelStub, "PreviousVisitModelMixin"]
    ):
        try:
            appointment = self.subject_visit.appointment
        except AttributeError:
            appointment = self.appointment
        visit_sequence = self.visit_sequence_cls(appointment=appointment)
        return visit_sequence.previous_visit

    class Meta:
        abstract = True
