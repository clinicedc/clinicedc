from typing import Any

from django.db import models
from django.db.models.deletion import PROTECT

from edc_appointment.appointment_status_updater import AppointmentStatusUpdater
from edc_appointment.constants import MISSED_APPT
from edc_consent.model_mixins import RequiresConsentFieldsModelMixin
from edc_constants.constants import NO, YES
from edc_document_status.model_mixins import DocumentStatusModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_metadata.model_mixins import MetadataHelperModelMixin
from edc_offstudy.model_mixins import OffstudyNonCrfModelMixin
from edc_visit_schedule.model_mixins import VisitScheduleModelMixin

from ...constants import MISSED_VISIT, NO_FOLLOW_UP_REASONS
from ...exceptions import RelatedVisitReasonError
from ...managers import VisitModelManager
from .previous_visit_model_mixin import PreviousVisitModelMixin
from .visit_model_fields_mixin import VisitModelFieldsMixin


class VisitModelMixin(
    VisitModelFieldsMixin,
    VisitScheduleModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    PreviousVisitModelMixin,
    DocumentStatusModelMixin,
    MetadataHelperModelMixin,
    OffstudyNonCrfModelMixin,
    RequiresConsentFieldsModelMixin,
    models.Model,
):
    """
    For example:

        class SubjectVisit(VisitModelMixin, CreatesMetadataModelMixin,
            BaseUuidModel):

            class Meta(VisitModelMixin.Meta):
                app_label = 'my_app'
    """

    metadata_helper_instance_attr = None

    appointment = models.OneToOneField("edc_appointment.appointment", on_delete=PROTECT)

    objects = VisitModelManager()

    def __str__(self) -> str:
        return f"{self.subject_identifier} {self.visit_code}.{self.visit_code_sequence}"

    def save(self: Any, *args, **kwargs):
        self.subject_identifier = self.appointment.subject_identifier
        self.visit_schedule_name = self.appointment.visit_schedule_name
        self.schedule_name = self.appointment.schedule_name
        self.visit_code = self.appointment.visit_code
        self.visit_code_sequence = self.appointment.visit_code_sequence
        self.require_crfs = NO if self.reason == MISSED_VISIT else YES
        if self.appointment.appt_timing == MISSED_APPT and self.reason != MISSED_VISIT:
            raise RelatedVisitReasonError(
                "Invalid. Appointment is missed. Expected visit to be missed also. "
                f"Got visit.reason=`{self.reason}`. See {self.appointment}. "
                "Perhaps catch this in the form."
            )
        if self.appointment.appt_timing != MISSED_APPT and self.reason == MISSED_VISIT:
            raise RelatedVisitReasonError(
                "Invalid. Appointment is not missed. Did not expected a missed visit. "
                f"Got visit.reason=`{self.reason}`. See {self.appointment}. "
                "Perhaps catch this in the form."
            )
        super().save(*args, **kwargs)

    def natural_key(self) -> tuple:
        return (
            self.subject_identifier,
            self.visit_schedule_name,
            self.schedule_name,
            self.visit_code,
            self.visit_code_sequence,
        )

    natural_key.dependencies = ("edc_appointment.appointment",)  # type:ignore

    @property
    def timepoint(self) -> int:
        return self.appointment.timepoint

    @staticmethod
    def get_visit_reason_no_follow_up_choices() -> dict:
        """Returns the visit reasons that do not imply any
        data collection; that is, the subject is not available.
        """
        dct = {}
        for item in NO_FOLLOW_UP_REASONS:
            dct.update({item: item})
        return dct

    def update_appointment_status(self) -> None:
        AppointmentStatusUpdater(self.appointment)

    class Meta(NonUniqueSubjectIdentifierFieldMixin.Meta):
        abstract = True
        unique_together = (
            (
                "subject_identifier",
                "visit_schedule_name",
                "schedule_name",
                "visit_code",
                "visit_code_sequence",
            ),
            (
                "subject_identifier",
                "visit_schedule_name",
                "schedule_name",
                "report_datetime",  # implies one visit per day!
            ),
        )
        indexes = (
            models.Index(
                fields=[
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                    "visit_code_sequence",
                    "report_datetime",
                ]
            ),
        )
