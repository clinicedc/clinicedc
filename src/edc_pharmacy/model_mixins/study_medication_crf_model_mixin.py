from __future__ import annotations

from edc_appointment.utils import get_next_appointment

from ..exceptions import NextRefillError
from ..refill import create_refills_from_crf
from .previous_model_mixin import PreviousNextModelMixin
from .study_medication_refill_model_mixin import StudyMedicationRefillModelMixin


class StudyMedicationCrfModelMixin(PreviousNextModelMixin, StudyMedicationRefillModelMixin):

    """Declare with field subject_visit using a CRF model mixin"""

    def save(self, *args, **kwargs):
        if not get_next_appointment(self.related_visit.appointment, include_interim=True):
            raise NextRefillError(
                "Cannot refill. This subject has no future appointments. "
                f"See {self.related_visit}."
            )
        if not self.refill_end_datetime:
            self.refill_end_datetime = get_next_appointment(
                self.related_visit.appointment, include_interim=True
            ).appt_datetime
        self.adjust_end_datetimes()
        self.number_of_days = (self.refill_end_datetime - self.refill_start_datetime).days
        super().save(*args, **kwargs)

    def creates_refills_from_crf(self) -> tuple:
        """Attribute called in signal"""
        return create_refills_from_crf(self, self.related_visit_model_attr())

    def get_subject_identifier(self):
        return self.related_visit.subject_identifier

    class Meta(StudyMedicationRefillModelMixin.Meta):
        abstract = True
