import uuid
from datetime import datetime
from typing import Union
from uuid import UUID

from django.conf import settings
from django.db import models
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_offstudy.model_mixins import OffstudyVisitModelMixin
from edc_timepoint.model_mixins import TimepointModelMixin
from edc_visit_schedule.model_mixins import VisitScheduleModelMixin

from ..choices import APPT_REASON, APPT_STATUS, APPT_TYPE
from ..constants import NEW_APPT
from ..exceptions import UnknownVisitCode
from ..managers import AppointmentManager
from ..stubs import AppointmentModelStub
from .appointment_methods_model_mixin import AppointmentMethodsModelMixin
from .window_period_model_mixin import WindowPeriodModelMixin

APPT_REASON = getattr(settings, "EDC_APPOINTMENT_APPT_REASON", APPT_REASON)


class AppointmentModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    AppointmentMethodsModelMixin,
    TimepointModelMixin,
    WindowPeriodModelMixin,
    VisitScheduleModelMixin,
    OffstudyVisitModelMixin,
):

    """Mixin for the appointment model only.

    Only one appointment per subject visit+visit_code_sequence.

    Attribute 'visit_code_sequence' should be populated by the system.
    """

    timepoint = models.DecimalField(
        null=True, decimal_places=1, max_digits=6, help_text="timepoint from schedule"
    )

    timepoint_datetime = models.DateTimeField(
        null=True, help_text="Unadjusted datetime calculated from visit schedule"
    )

    appt_close_datetime = models.DateTimeField(
        null=True,
        help_text=(
            "timepoint_datetime adjusted according to the nearest "
            "available datetime for this facility"
        ),
    )

    facility_name = models.CharField(
        max_length=25,
        help_text="set by model that creates appointments, e.g. Enrollment",
    )

    appt_datetime = models.DateTimeField(
        verbose_name="Appointment date and time", db_index=True
    )

    appt_type = models.CharField(
        verbose_name="Appointment type",
        choices=APPT_TYPE,
        default="clinic",
        max_length=20,
        help_text="Default for subject may be edited Subject Configuration.",
    )

    appt_status = models.CharField(
        verbose_name="Status",
        choices=APPT_STATUS,
        max_length=25,
        default=NEW_APPT,
        db_index=True,
        help_text=(
            "If the visit has already begun, only 'in progress', "
            "'incomplete' or 'done' are valid options"
        ),
    )

    appt_reason = models.CharField(
        verbose_name="Reason for appointment",
        max_length=25,
        choices=APPT_REASON,
        help_text=(
            "The visit report's `reason for visit` will be validated against this. "
            "Refer to the protocol's documentation for the definition of a `scheduled` visit."
        ),
    )

    comment = models.CharField("Comment", max_length=250, blank=True)

    is_confirmed = models.BooleanField(default=False, editable=False)

    objects = AppointmentManager()

    def __str__(self) -> str:
        return f"{self.visit_code}.{self.visit_code_sequence}"

    def natural_key(self) -> tuple:
        return (
            self.subject_identifier,
            self.visit_schedule_name,
            self.schedule_name,
            self.visit_code,
            self.visit_code_sequence,
        )

    @property
    def str_pk(self: AppointmentModelStub) -> Union[str, uuid.UUID]:
        if isinstance(self.id, UUID):
            return str(self.pk)
        return self.pk

    @property
    def title(self: AppointmentModelStub) -> str:
        if not self.schedule.visits.get(self.visit_code):
            valid_visit_codes = [v for v in self.schedule.visits]
            raise UnknownVisitCode(
                "Unknown visit code specified for existing apointment instance. "
                "Has the visit schedule changed? Expected one of "
                f"{valid_visit_codes}. Got {self.visit_code}. "
                f"See {self}."
            )
        title = self.schedule.visits.get(self.visit_code).title
        if self.visit_code_sequence > 0:
            title = f"{title}.{self.visit_code_sequence}"
        return title

    @property
    def report_datetime(self: AppointmentModelStub) -> datetime:
        return self.appt_datetime

    class Meta:
        abstract = True
        unique_together = (
            (
                "subject_identifier",
                "visit_schedule_name",
                "schedule_name",
                "visit_code",
                "timepoint",
                "visit_code_sequence",
            ),
        )
        ordering = ("timepoint", "visit_code_sequence")

        indexes = [
            models.Index(
                fields=[
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                    "timepoint",
                    "visit_code_sequence",
                ]
            )
        ]
