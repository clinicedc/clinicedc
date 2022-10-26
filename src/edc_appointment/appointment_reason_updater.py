from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import INCOMPLETE
from edc_metadata import KEYED
from edc_metadata.metadata_helper import MetadataHelperMixin
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED, UNSCHEDULED
from edc_visit_tracking.utils import (
    get_subject_visit_missed_model,
    get_subject_visit_missed_model_cls,
)

from .choices import APPT_TIMING
from .constants import MISSED_APPT, SCHEDULED_APPT, UNSCHEDULED_APPT
from .exceptions import (
    AppointmentBaselineError,
    AppointmentReasonUpdaterCrfsExistsError,
    AppointmentReasonUpdaterError,
    AppointmentReasonUpdaterRequisitionsExistsError,
    UnscheduledAppointmentError,
)
from .utils import raise_on_appt_may_not_be_missed

if TYPE_CHECKING:
    from edc_visit_tracking.model_mixins import VisitModelMixin

    from .models import Appointment


class AppointmentReasonUpdater(MetadataHelperMixin):
    """A class to try to update `reason` field based on the
    response from appointment timing and appointment reason.

    See also the Appointment signal that creates
    the related visit instance, if it does not exist
    when appt_timing==MISSED_APPT. (missed_appointment)

    See also the Appointment signal that deletes
    a related visit for a cancelled appointment.
    (cancelled_appointment)

    """

    metadata_helper_instance_attr: str = "appointment"

    def __init__(
        self,
        appointment: Appointment = None,
        appt_timing: str = None,
        appt_reason: str = None,
        commit: bool | None = None,
    ):
        self._related_visit = None
        self.appointment = appointment
        if not getattr(self.appointment, "id", None):
            raise AppointmentReasonUpdaterError(
                "Appointment instance must exist. Got `id` is None"
            )
        self.commit = commit
        self.appt_timing = appt_timing or self.appointment.appt_timing
        if self.appt_timing not in [a for a, b in APPT_TIMING]:
            raise AppointmentReasonUpdaterError(
                f"Invalid value for appt_timing. "
                f"Expected on of {[a for a, b in APPT_TIMING]}. Got {self.appt_timing}"
            )
        try:
            raise_on_appt_may_not_be_missed(
                appointment=appointment, appt_timing=self.appt_timing
            )
        except (AppointmentBaselineError, UnscheduledAppointmentError) as e:
            raise AppointmentReasonUpdaterError(e)

        self.appt_reason = appt_reason or self.appointment.appt_reason

        self.update_related_visit_or_raise()

    def update_related_visit_or_raise(self) -> None:
        if self.related_visit:
            if self.appt_timing == MISSED_APPT and self.appt_reason in [
                SCHEDULED_APPT,
                UNSCHEDULED_APPT,
            ]:
                self.update_related_visit_to_missed_or_raise()
            elif self.appt_timing != MISSED_APPT and self.appt_reason in [
                SCHEDULED_APPT,
                UNSCHEDULED_APPT,
            ]:
                self.update_related_visit_to_not_missed_or_raise()
            else:
                raise AppointmentReasonUpdaterError(
                    f"Condition not handled. Got appt_reason={self.appt_reason}, "
                    f"appt_timing={self.appt_timing}"
                )

    @property
    def related_visit(self) -> VisitModelMixin | None:
        if not self._related_visit:
            try:
                self._related_visit = getattr(
                    self.appointment, self.appointment.related_visit_model_attr()
                )
            except ObjectDoesNotExist:
                self._related_visit = None
            except AttributeError as e:
                if "related_visit_model_attr" not in str(e):
                    raise
                self._related_visit = None
        return self._related_visit

    def update_related_visit_to_missed_or_raise(self) -> None:
        self.raise_if_keyed_data_exists()
        if self.related_visit:
            if self.appt_timing != MISSED_APPT:
                raise AppointmentReasonUpdaterError(
                    f"Appointment is not missed. Got appt_timing=`{self.appt_timing}` "
                    f"See {self.appointment}."
                )
            self.related_visit.reason = MISSED_VISIT
            self.related_visit.document_status = INCOMPLETE
            if self.commit:
                # the signal to update metadata is called on post_save
                self.related_visit.save_base(
                    update_fields=["reason", "document_status", "comments"]
                )
                self.related_visit.refresh_from_db()

    def update_related_visit_to_not_missed_or_raise(self) -> None:
        """Updates the subject visit instance from MISSED_VISIT
        to SCHEDULED or UNSCHEDULED.
        """
        if self.related_visit:
            reason = self.get_reason_from_appt_reason(self.appt_reason)
            if self.appt_timing == MISSED_APPT:
                raise AppointmentReasonUpdaterError(
                    f"Appointment is missed. Got appt_timing=`{self.appt_timing}` "
                    f"See {self.appointment}."
                )
            self.delete_subject_visit_missed_if_exists()
            self.related_visit.reason = reason
            self.related_visit.document_status = INCOMPLETE
            if self.related_visit.comments:
                self.related_visit.comments = self.related_visit.comments.replace(
                    "[auto-created]", ""
                )
            if self.commit:
                # the signal to update metadata is called on post_save
                # see also `update_document_status_on_save`
                self.related_visit.save_base(
                    update_fields=["reason", "document_status", "comments"]
                )
                self.related_visit.refresh_from_db()

    def raise_if_keyed_data_exists(self) -> None:
        """Raises an exception if CRF or Requisition metadata exists"""
        if self.crf_metadata_keyed_exists:
            if not self.crf_metadata_keyed_is_subject_visit_missed_only:
                raise AppointmentReasonUpdaterCrfsExistsError(
                    "Invalid. CRFs have already been entered for this timepoint."
                )
        elif self.requisition_metadata_keyed_exists:
            raise AppointmentReasonUpdaterRequisitionsExistsError(
                "Invalid. Requisitions have already been entered " "for this timepoint."
            )

    @property
    def crf_metadata_keyed_is_subject_visit_missed_only(self) -> bool:
        """Returns True if the only keyed CRF is the subject
        visit missed model.
        """
        return (
            self.get_crf_metadata_by(KEYED).count() == 1
            and self.get_crf_metadata_by(KEYED)[0].model == get_subject_visit_missed_model()
        )

    def delete_subject_visit_missed_if_exists(self) -> None:
        """Deletes the subject visit missed report if it exists"""
        get_subject_visit_missed_model_cls().objects.filter(
            subject_visit__appointment=self.appointment
        ).delete()

    def get_reason_from_appt_reason(self, appt_reason: str) -> str:
        """Returns a subject visit reason given the appt reason"""
        if appt_reason == SCHEDULED_APPT:
            visit_reason = SCHEDULED
        elif appt_reason == UNSCHEDULED_APPT and self.appointment.visit_code_sequence > 0:
            visit_reason = UNSCHEDULED
        else:
            raise AppointmentReasonUpdaterError(
                "Update failed. This is not an unscheduled appointment. "
                f"Got visit_code_sequence > 0 for appt_reason={appt_reason}"
            )
        return visit_reason
