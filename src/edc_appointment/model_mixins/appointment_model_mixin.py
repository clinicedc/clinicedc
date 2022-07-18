import uuid
from datetime import datetime
from typing import Union
from uuid import UUID

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from edc_document_status.model_mixins import DocumentStatusModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_metadata.model_mixins import MetadataHelperModelMixin
from edc_offstudy.model_mixins import OffstudyVisitModelMixin
from edc_timepoint.model_mixins import TimepointModelMixin
from edc_utils import formatted_datetime
from edc_visit_schedule import site_visit_schedules
from edc_visit_schedule.model_mixins import VisitScheduleModelMixin
from edc_visit_schedule.subject_schedule import NotOnScheduleError
from edc_visit_schedule.utils import is_baseline

from ..choices import APPT_STATUS, APPT_TIMING, APPT_TYPE, DEFAULT_APPT_REASON_CHOICES
from ..constants import IN_PROGRESS_APPT, NEW_APPT, ONTIME_APPT
from ..exceptions import UnknownVisitCode
from ..managers import AppointmentManager
from ..stubs import AppointmentModelStub
from ..utils import update_appt_status
from .appointment_methods_model_mixin import AppointmentMethodsModelMixin
from .missed_appointment_model_mixin import MissedAppointmentModelMixin
from .window_period_model_mixin import WindowPeriodModelMixin


class AppointmentModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    AppointmentMethodsModelMixin,
    TimepointModelMixin,
    MissedAppointmentModelMixin,
    WindowPeriodModelMixin,
    VisitScheduleModelMixin,
    DocumentStatusModelMixin,
    MetadataHelperModelMixin,
    OffstudyVisitModelMixin,
):

    metadata_helper_instance_attr = None

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
            "'incomplete' or 'done' are valid options. Only unscheduled appointments "
            "may be cancelled."
        ),
    )

    appt_reason = models.CharField(
        verbose_name="Reason for appointment",
        max_length=25,
        choices=DEFAULT_APPT_REASON_CHOICES,
        help_text=(
            "The visit report's `reason for visit` will be validated against this. "
            "Refer to the protocol's documentation for the definition of a `scheduled` "
            "appointment."
        ),
    )

    appt_timing = models.CharField(
        verbose_name="Timing",
        max_length=25,
        choices=APPT_TIMING,
        default=ONTIME_APPT,
        help_text=(
            "If late, you may be required to complete a Protocol Deviation / Violation form. "
            "Refer to the protocol/SOP for the definition of scheduled appointment "
            "window periods."
        ),
    )

    comment = models.CharField("Comment", max_length=250, blank=True)

    is_confirmed = models.BooleanField(default=False, editable=False)

    ignore_window_period = models.BooleanField(default=False, editable=False)

    objects = AppointmentManager()

    def __str__(self) -> str:
        return f"{self.visit_code}.{self.visit_code_sequence}"

    def save(self, *args, **kwargs):
        if not kwargs.get("update_fields", None):
            if self.id and is_baseline(instance=self):
                visit_schedule = site_visit_schedules.get_visit_schedule(
                    self.visit_schedule_name
                )
                schedule = visit_schedule.schedules.get(self.schedule_name)
                try:
                    onschedule_obj = django_apps.get_model(
                        schedule.onschedule_model
                    ).objects.get(
                        subject_identifier=self.subject_identifier,
                        onschedule_datetime__lte=self.appt_datetime,
                    )
                except ObjectDoesNotExist as e:
                    dte_as_str = formatted_datetime(self.appt_datetime)
                    raise NotOnScheduleError(
                        "Subject is not on a schedule. Using subject_identifier="
                        f"`{self.subject_identifier}` and appt_datetime=`{dte_as_str}`. Got {e}"
                    )
                if self.appt_datetime == onschedule_obj.onschedule_datetime:
                    pass
                elif self.appt_datetime > onschedule_obj.onschedule_datetime:
                    # update appointment timepoints
                    schedule.put_on_schedule(
                        subject_identifier=self.subject_identifier,
                        onschedule_datetime=self.appt_datetime,
                        skip_baseline=True,
                    )
            self.update_subject_visit_reason_or_raise()
            if self.appt_status != IN_PROGRESS_APPT and getattr(
                settings, "EDC_APPOINTMENT_CHECK_APPT_STATUS", True
            ):
                update_appt_status(self)
        super().save(*args, **kwargs)

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
                "Has the appointments schedule changed? Expected one of "
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
