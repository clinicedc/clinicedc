from __future__ import annotations

from ..exceptions import NextRefillError
from ..refill import create_refills_from_crf
from .previous_model_mixin import PreviousNextModelMixin
from .study_medication_refill_model_mixin import StudyMedicationRefillModelMixin


class StudyMedicationCrfModelMixin(PreviousNextModelMixin, StudyMedicationRefillModelMixin):

    """Declare with field subject_visit using a CRF model mixin"""

    def save(self, *args, **kwargs):
        if not self.subject_visit.appointment.next:
            raise NextRefillError("Cannot refill. This subject has no future appointments.")
        if not self.refill_end_datetime:
            raise NextRefillError("Cannot refill. Refill has not end datetime.")
        self.adjust_end_datetimes()
        self.number_of_days = (self.refill_end_datetime - self.refill_start_datetime).days
        super().save(*args, **kwargs)

    def creates_refills_from_crf(self) -> tuple:
        """Attribute called in signal"""
        return create_refills_from_crf(self, self.visit_model_attr())

    def get_subject_identifier(self):
        return getattr(self, self.visit_model_attr()).subject_identifier

    # @property
    # def rx(self):
    #     return get_rx_model_cls().objects.get(
    #         subject_identifier=self.get_subject_identifier(),
    #         medications__in=[self.formulation.medication],
    #         rx_date__lte=self.refill_start_datetime.date(),
    #         # rx_expiration_date__gte=self.refill_start_datetime.date(),
    #     )

    class Meta(StudyMedicationRefillModelMixin.Meta):
        abstract = True
