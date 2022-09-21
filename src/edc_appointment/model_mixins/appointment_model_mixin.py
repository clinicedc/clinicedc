from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Union
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

from ..constants import IN_PROGRESS_APPT
from ..exceptions import UnknownVisitCode
from ..managers import AppointmentManager
from ..utils import update_appt_status
from .appointment_fields_model_mixin import AppointmentFieldsModelMixin
from .appointment_methods_model_mixin import AppointmentMethodsModelMixin
from .missed_appointment_model_mixin import MissedAppointmentModelMixin
from .window_period_model_mixin import WindowPeriodModelMixin

if TYPE_CHECKING:
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
    OffstudyVisitModelMixin,
):

    """Mixin for the appointment model only.

    Only one appointment per subject visit+visit_code_sequence.

    Attribute 'visit_code_sequence' should be populated by the system.
    """

    metadata_helper_instance_attr = None

    objects = AppointmentManager()

    def __str__(self) -> str:
        return f"{self.subject_identifier} {self.visit_code}.{self.visit_code_sequence}"

    def save(self: Appointment, *args, **kwargs):
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
                        f"`{self.subject_identifier}` and appt_datetime=`{dte_as_str}`."
                        f"Got {e}"
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
    def str_pk(self: Appointment) -> Union[str, uuid.UUID]:
        if isinstance(self.id, UUID):
            return str(self.pk)
        return self.pk

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
