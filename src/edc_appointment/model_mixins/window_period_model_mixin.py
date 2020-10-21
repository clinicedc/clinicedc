from django.db import models
from edc_visit_schedule.schedule.window import (
    ScheduledVisitWindowError,
    UnScheduledVisitWindowError,
)


class AppointmentWindowError(Exception):
    pass


class WindowPeriodModelMixin(models.Model):
    """A model mixin declared with the Appointment model to managed
    window period calculations for appt_datetime.
    """

    window_period_checks_enabled = True

    def save(self, *args, **kwargs):
        if self.id and self.appt_datetime and self.timepoint_datetime:
            self.raise_on_not_datetime_in_window()
        super().save(*args, **kwargs)

    def raise_on_not_datetime_in_window(self):
        if not self.is_baseline_appt:
            baseline_timepoint_datetime = self.__class__.objects.first_appointment(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
            ).timepoint_datetime
            try:
                self.schedule.datetime_in_window(
                    dt=self.appt_datetime,
                    timepoint_datetime=self.timepoint_datetime,
                    visit_code=self.visit_code,
                    visit_code_sequence=self.visit_code_sequence,
                    baseline_timepoint_datetime=baseline_timepoint_datetime,
                )
            except ScheduledVisitWindowError as e:
                msg = str(e)
                msg.replace("Invalid datetime", "Invalid appointment datetime")
                msg = f"{msg} Perhaps catch this in the form."
                raise AppointmentWindowError(msg)
            except UnScheduledVisitWindowError as e:
                msg = str(e)
                msg.replace("Invalid datetime", "Invalid appointment datetime")
                msg = f"{msg} Perhaps catch this in the form."
                raise AppointmentWindowError(msg)

    @property
    def is_baseline_appt(self):
        return self.timepoint == 0 and self.visit_code_sequence == 0

    class Meta:
        abstract = True
