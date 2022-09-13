from __future__ import annotations

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_appointment.utils import get_next_appointment
from edc_constants.constants import YES

from ..refill import create_refills_from_crf
from .previous_model_mixin import PreviousNextModelMixin
from .study_medication_refill_model_mixin import StudyMedicationRefillModelMixin


class StudyMedicationError(Exception):
    pass


class NextStudyMedicationError(Exception):
    pass


class StudyMedicationCrfModelMixin(PreviousNextModelMixin, StudyMedicationRefillModelMixin):

    """Declare with field subject_visit using a CRF model mixin"""

    def save(self, *args, **kwargs):
        if not self.formulation:
            raise StudyMedicationError(f"Formulation cannot be None. See {self}")
        if not self.dosage_guideline:
            raise StudyMedicationError(f"Dosage guideline cannot be None. See {self}")
        if not get_next_appointment(self.related_visit.appointment, include_interim=True):
            raise NextStudyMedicationError(
                "Cannot refill. This subject has no future appointments. "
                f"See {self.related_visit}."
            )
        if not self.refill_end_datetime:
            self.refill_end_datetime = get_next_appointment(
                self.related_visit.appointment, include_interim=True
            ).appt_datetime
        self.adjust_end_datetimes()
        self.number_of_days = (self.refill_end_datetime - self.refill_start_datetime).days
        if not self.rx:
            raise StudyMedicationError(f"Prescription not found. See {self}")
        if self.order_or_update_next == YES:
            self.validate_or_raise_for_next_refill()
        super().save(*args, **kwargs)

    def creates_refills_from_crf(self) -> tuple:
        """Attribute called in signal"""
        return create_refills_from_crf(self, self.related_visit_model_attr())

    def get_subject_identifier(self):
        return self.related_visit.subject_identifier

    @property
    def rx(self):
        try:
            rx = django_apps.get_model("edc_pharmacy.rx").objects.get(
                registered_subject__subject_identifier=self.related_visit.subject_identifier,
                medications__in=[self.formulation.medication],
                rx_date__lte=self.refill_start_datetime.date(),
            )
        except ObjectDoesNotExist:
            return None
        else:
            if (
                rx.rx_expiration_date
                and rx.rx_expiration_date < self.refill_end_datetime.date()
            ):
                raise StudyMedicationError(f"Prescription is expired. Got {rx}. See {self}.")
        return rx

    def validate_or_raise_for_next_refill(self) -> None:
        if self.order_or_update_next == YES:
            if not self.next_formulation:
                raise NextStudyMedicationError(
                    "Cannot create next refill. Next formulation is none. "
                    "Perhaps catch this in the form."
                )
            if not self.next_dosage_guideline:
                raise NextStudyMedicationError(
                    "Cannot create next refill. Next dosage guideline is none. "
                    "Perhaps catch this in the form."
                )

    class Meta(StudyMedicationRefillModelMixin.Meta):
        abstract = True
