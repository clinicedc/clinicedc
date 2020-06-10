from django.apps import apps as django_apps
from django.db import models
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_offstudy.model_mixins import OffstudyVisitModelMixin
from edc_timepoint.model_mixins import TimepointModelMixin
from edc_visit_schedule.model_mixins import VisitScheduleModelMixin
from uuid import UUID

from edc_visit_tracking.constants import MISSED_VISIT

from ..choices import APPT_TYPE, APPT_STATUS, APPT_REASON
from ..constants import NEW_APPT
from ..managers import AppointmentManager
from .appointment_methods_model_mixin import AppointmentMethodsModelMixin


class AppointmentModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    AppointmentMethodsModelMixin,
    TimepointModelMixin,
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
        verbose_name=("Appointment date and time"), db_index=True
    )

    appt_type = models.CharField(
        verbose_name="Appointment type",
        choices=APPT_TYPE,
        default="clinic",
        max_length=20,
        help_text=("Default for subject may be edited Subject Configuration."),
    )

    appt_status = models.CharField(
        verbose_name=("Status"),
        choices=APPT_STATUS,
        max_length=25,
        default=NEW_APPT,
        db_index=True,
        help_text=(
            "If the visit has already begun, only 'in progress' or "
            "'incomplete' are valid options"
        ),
    )

    appt_reason = models.CharField(
        verbose_name=("Reason for appointment"), max_length=25, choices=APPT_REASON
    )

    comment = models.CharField("Comment", max_length=250, blank=True)

    is_confirmed = models.BooleanField(default=False, editable=False)

    objects = AppointmentManager()

    def __str__(self):
        return f"{self.visit_code}.{self.visit_code_sequence}"

    def natural_key(self):
        return (
            self.subject_identifier,
            self.visit_schedule_name,
            self.schedule_name,
            self.visit_code,
            self.visit_code_sequence,
        )

    @property
    def str_pk(self):
        if isinstance(self.id, UUID):
            return str(self.pk)
        return self.pk

    @property
    def title(self):
        title = self.schedule.visits.get(self.visit_code).title
        if self.visit_code_sequence > 0:
            title = f"{title}.{self.visit_code_sequence}"
        return title

    @property
    def facility(self):
        """Returns the facility instance for this facility name.
        """
        app_config = django_apps.get_app_config("edc_facility")
        return app_config.get_facility(name=self.facility_name)

    @property
    def report_datetime(self):
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
