from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_appointment.utils import get_next_appointment
from edc_constants.constants import YES
from edc_utils import formatted_datetime

from ..exceptions import NextStudyMedicationError, StudyMedicationError
from ..refill import create_refills_from_crf
from .previous_model_mixin import PreviousNextModelMixin
from .study_medication_refill_model_mixin import StudyMedicationRefillModelMixin

if TYPE_CHECKING:
    from ..models import RxRefill


class StudyMedicationCrfModelMixin(PreviousNextModelMixin, StudyMedicationRefillModelMixin):

    """Declare with field subject_visit using a CRF model mixin"""

    def save(self, *args, **kwargs):
        if not self.formulation:
            raise StudyMedicationError(
                f"Formulation cannot be None. Perhaps catch this in the form. See {self}."
            )
        if not self.dosage_guideline:
            raise StudyMedicationError(
                f"Dosage guideline cannot be None. Perhaps catch this in the form. See {self}."
            )

        if self.refill_to_next_visit == YES and not get_next_appointment(
            self.related_visit.appointment, include_interim=True
        ):
            raise NextStudyMedicationError(
                "Cannot refill to next appointment. This subject has no future appointments. "
                f"Perhaps catch this in the form. See {self.related_visit}."
            )

        if not self.refill_end_datetime:
            if self.refill_to_next_visit == YES:
                self.refill_end_datetime = get_next_appointment(
                    self.related_visit.appointment, include_interim=True
                ).appt_datetime
            else:
                self.refill_end_datetime = self.refill_start_datetime

        self.adjust_end_datetimes()

        self.number_of_days = (self.refill_end_datetime - self.refill_start_datetime).days

        if not self.rx:
            dt = formatted_datetime(self.refill_start_datetime)
            if not self.rx_model_cls.objects.filter(
                subject_identifier=self.related_visit.subject_identifier,
            ).exists():
                error_msg = (
                    f"No prescriptions found for this subject. "
                    f"Using subject_identifier=`{self.related_visit.subject_identifier}` "
                    f"Perhaps catch this in the form. See {self}."
                )
            elif not self.rx_model_cls.objects.filter(
                subject_identifier=self.related_visit.subject_identifier,
                medications__in=[self.formulation.medication],
            ).exists():
                error_msg = (
                    f"No prescriptions found for this medication. "
                    f"Using medication {self.formulation.medication}. "
                    f"Perhaps catch this in the form. See {self}."
                )
            else:
                error_msg = (
                    f"A valid prescription not found. Check refill date. "
                    f"Using refill start datetime `{dt}`. "
                    f"Perhaps catch this in the form. See {self}."
                )

            raise StudyMedicationError(error_msg)

        super().save(*args, **kwargs)

    def creates_refills_from_crf(self) -> Tuple[RxRefill, RxRefill | None]:
        """Attribute called in signal"""
        return create_refills_from_crf(self, self.related_visit_model_attr())

    def get_subject_identifier(self):
        return self.related_visit.subject_identifier

    @property
    def rx_model_cls(self):
        return django_apps.get_model("edc_pharmacy.rx")

    @property
    def rx(self):
        try:
            rx = self.rx_model_cls.objects.get(
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
                raise StudyMedicationError(
                    f"Prescription is expired. Got {rx}. Perhaps catch this in the form. "
                    f"See {self}."
                )
        return rx

    class Meta(StudyMedicationRefillModelMixin.Meta):
        abstract = True
