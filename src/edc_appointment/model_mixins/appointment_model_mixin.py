from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Union
from uuid import UUID

from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import UniqueConstraint
from edc_document_status.model_mixins import DocumentStatusModelMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_metadata.model_mixins import MetadataHelperModelMixin
from edc_offstudy.model_mixins import OffstudyNonCrfModelMixin
from edc_timepoint.model_mixins import TimepointModelMixin
from edc_utils import formatted_datetime, to_utc
from edc_visit_schedule.model_mixins import VisitScheduleModelMixin
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.subject_schedule import NotOnScheduleError
from edc_visit_schedule.utils import is_baseline

from ..constants import CANCELLED_APPT, IN_PROGRESS_APPT
from ..exceptions import AppointmentDatetimeError, UnknownVisitCode
from ..managers import AppointmentManager
from ..utils import raise_on_appt_may_not_be_missed, update_appt_status
from .appointment_fields_model_mixin import AppointmentFieldsModelMixin
from .appointment_methods_model_mixin import AppointmentMethodsModelMixin
from .missed_appointment_model_mixin import MissedAppointmentModelMixin
from .window_period_model_mixin import WindowPeriodModelMixin

if TYPE_CHECKING:
    from edc_visit_schedule.schedule import Schedule

    from ..models import Appointment


class AppointmentModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    AppointmentFieldsModelMixin,
    AppointmentMethodsModelMixin,
    TimepointModelMixin,
    MissedAppointmentModelMixin,
    WindowPeriodModelMixin,
    VisitScheduleModelMixin,
    DocumentStatusModelMixin,
    MetadataHelperModelMixin,
    OffstudyNonCrfModelMixin,
):
    """Mixin for the appointment model only.

    Only one appointment per subject visit+visit_code_sequence.

    Attribute 'visit_code_sequence' should be populated by the system.
    """

    metadata_helper_instance_attr = None

    offschedule_compare_dates_as_datetimes = False

    objects = AppointmentManager()

    def __str__(self) -> str:
        return f"{self.subject_identifier} {self.visit_code}.{self.visit_code_sequence}"

    def save(self: Appointment, *args, **kwargs):
        if not kwargs.get("update_fields", None):
            if self.id and is_baseline(instance=self):
                visit_schedule = site_visit_schedules.get_visit_schedule(
                    self.visit_schedule_name
                )
                schedule: Schedule = visit_schedule.schedules.get(self.schedule_name)
                try:
                    onschedule_obj = django_apps.get_model(
                        schedule.onschedule_model
                    ).objects.get(
                        subject_identifier=self.subject_identifier,
                        onschedule_datetime__lte=to_utc(self.appt_datetime)
                        + relativedelta(seconds=1),
                    )
                except ObjectDoesNotExist as e:
                    dte_as_str = formatted_datetime(self.appt_datetime)
                    raise NotOnScheduleError(
                        "Subject is not on a schedule. Using subject_identifier="
                        f"`{self.subject_identifier}` and appt_datetime=`{dte_as_str}`."
                        f"Got {e}"
                    )
                if self.appt_datetime > onschedule_obj.onschedule_datetime:
                    # update appointment timepoints
                    schedule.put_on_schedule(
                        subject_identifier=self.subject_identifier,
                        onschedule_datetime=to_utc(self.appt_datetime),
                        skip_baseline=True,
                    )
            else:
                # self.validate_appt_datetime_not_before_previous()
                self.validate_appt_datetime_not_after_next()
            raise_on_appt_may_not_be_missed(appointment=self)
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
    def str_pk(self: Appointment) -> Union[str, uuid.UUID]:
        if isinstance(self.id, UUID):
            return str(self.pk)
        return self.pk

    def validate_appt_datetime_not_before_previous(self) -> None:
        if self.appt_status != CANCELLED_APPT and self.appt_datetime:
            if (
                self.relative_previous
                and self.appt_datetime <= self.relative_previous.appt_datetime
            ):
                appt_datetime = formatted_datetime(self.appt_datetime)
                previous_appt_datetime = formatted_datetime(
                    self.relative_previous.appt_datetime
                )
                raise AppointmentDatetimeError(
                    "Datetime cannot be on or before previous appointment datetime. "
                    f"Got {appt_datetime} <= {previous_appt_datetime}. "
                    f"See appointment `{self}` and "
                    f"`{self.relative_previous}`."
                )

    def validate_appt_datetime_not_after_next(self) -> None:
        if self.appt_status != CANCELLED_APPT and self.appt_datetime and self.relative_next:
            if self.appt_datetime >= self.relative_next.appt_datetime:
                appt_datetime = formatted_datetime(self.appt_datetime)
                next_appt_datetime = formatted_datetime(self.relative_next.appt_datetime)
                raise AppointmentDatetimeError(
                    "Datetime cannot be on or after next appointment datetime. "
                    f"Got {appt_datetime} >= {next_appt_datetime}. "
                    f"See appointment `{self}` and "
                    f"`{self.relative_next}`."
                )

    @property
    def title(self: Appointment) -> str:
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
    def report_datetime(self: Appointment) -> datetime:
        return self.appt_datetime

    class Meta(NonUniqueSubjectIdentifierFieldMixin.Meta):
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=[
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                    "timepoint",
                    "visit_code_sequence",
                ],
                name="unique_%(app_label)s_%(class)s_100",
            ),
            UniqueConstraint(
                fields=[
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "appt_datetime",
                ],
                name="unique_%(app_label)s_%(class)s_200",
            ),
        ]
        indexes = [
            models.Index(fields=["appt_datetime"]),
            models.Index(fields=["appt_status"]),
            models.Index(fields=["timepoint", "visit_code_sequence"]),
            models.Index(fields=["subject_identifier", "appt_reason"]),
            models.Index(
                fields=["site", "subject_identifier", "timepoint", "visit_code_sequence"]
            ),
            models.Index(
                fields=[
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                    "appt_reason",
                    "timepoint",
                    "visit_code_sequence",
                ]
            ),
        ]
