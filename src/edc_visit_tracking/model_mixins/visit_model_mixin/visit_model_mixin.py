from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.constants import IN_PROGRESS_APPT, COMPLETE_APPT
from edc_constants.constants import YES, NO
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_visit_schedule.model_mixins import VisitScheduleModelMixin

from ...constants import NO_FOLLOW_UP_REASONS, MISSED_VISIT
from ...managers import VisitModelManager
from ..previous_visit_model_mixin import PreviousVisitModelMixin
from .visit_model_fields_mixin import VisitModelFieldsMixin


class VisitModelMixin(
    VisitModelFieldsMixin,
    VisitScheduleModelMixin,
    NonUniqueSubjectIdentifierFieldMixin,
    PreviousVisitModelMixin,
    models.Model,
):

    """
    For example:

        class SubjectVisit(VisitModelMixin, CreatesMetadataModelMixin,
                           RequiresConsentModelMixin, BaseUuidModel):

            class Meta(VisitModelMixin.Meta):
                app_label = 'my_app'
    """

    appointment = models.OneToOneField("edc_appointment.appointment", on_delete=PROTECT)

    objects = VisitModelManager()

    def __str__(self):
        return f"{self.subject_identifier} {self.visit_code}.{self.visit_code_sequence}"

    def save(self, *args, **kwargs):
        self.subject_identifier = self.appointment.subject_identifier
        self.visit_schedule_name = self.appointment.visit_schedule_name
        self.schedule_name = self.appointment.schedule_name
        self.visit_code = self.appointment.visit_code
        self.visit_code_sequence = self.appointment.visit_code_sequence
        # TODO: may be a problem with crfs_missed
        self.require_crfs = NO if self.reason == MISSED_VISIT else YES
        super().save(*args, **kwargs)

    def natural_key(self):
        return (
            self.subject_identifier,
            self.visit_schedule_name,
            self.schedule_name,
            self.visit_code,
            self.visit_code_sequence,
        )

    natural_key.dependencies = ["edc_appointment.appointment"]

    @property
    def timepoint(self):
        return self.appointment.timepoint

    def get_visit_reason_no_follow_up_choices(self):
        """Returns the visit reasons that do not imply any
        data collection; that is, the subject is not available.
        """
        dct = {}
        for item in NO_FOLLOW_UP_REASONS:
            dct.update({item: item})
        return dct

    def post_save_check_appointment_in_progress(self):
        if self.reason in self.get_visit_reason_no_follow_up_choices():
            if self.appointment.appt_status != COMPLETE_APPT:
                self.appointment.appt_status = COMPLETE_APPT
                self.appointment.save()
        else:
            if self.appointment.appt_status != IN_PROGRESS_APPT:
                self.appointment.appt_status = IN_PROGRESS_APPT
                self.appointment.save()

    class Meta:
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
                "report_datetime",
            ),
        )
        ordering = (
            "subject_identifier",
            "visit_schedule_name",
            "schedule_name",
            "visit_code",
            "visit_code_sequence",
            "report_datetime",
        )

        indexes = [
            models.Index(
                fields=[
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                    "visit_code_sequence",
                    "report_datetime",
                ]
            )
        ]
