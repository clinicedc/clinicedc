from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from django.db import models
from django.db.models import PROTECT
from django.utils.translation import gettext_lazy as _
from edc_constants.choices import YES_NO
from edc_constants.constants import NO
from edc_facility.utils import get_health_facility_model

from edc_appointment.utils import validate_date_is_on_clinic_day

__all__ = ["NextAppointmentCrfModelMixin"]


class NextAppointmentCrfModelMixin(models.Model):

    offschedule_today = models.CharField(
        verbose_name=_("Is the subject going off schedule today?"),
        choices=YES_NO,
        default=NO,
        max_length=15,
        help_text=_("If going off schedule today, additional CRFs will be added for today."),
    )

    appt_date = models.DateField(
        verbose_name=_("Next scheduled routine/facility appointment"),
        help_text=_("Should fall on an valid clinic day for this facility"),
        null=True,
        blank=True,
    )

    appt_datetime = models.DateTimeField(null=True, editable=False)

    info_source = models.ForeignKey(
        "edc_appointment.infosources",
        verbose_name=_("What is the source of this appointment date"),
        max_length=15,
        on_delete=PROTECT,
        null=True,
        blank=True,
    )

    # named this way to not conflict with property `visit_schedule`
    # see also edc-crf
    visitschedule = models.ForeignKey(
        "edc_visit_schedule.VisitSchedule",
        on_delete=PROTECT,
        verbose_name=_("Which study visit code is closest to this appointment date"),
        max_length=15,
        null=True,
        blank=True,
        help_text=_(
            "Click SAVE to let the EDC suggest. Once selected, interim appointments will "
            "be flagged as not required/missed."
        ),
    )

    health_facility = models.ForeignKey(
        get_health_facility_model(),
        on_delete=PROTECT,
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if self.appt_date:
            self.appt_datetime = datetime(
                self.appt_date.year,
                self.appt_date.month,
                self.appt_date.day,
                7,
                30,
                0,
                tzinfo=ZoneInfo("UTC"),
            )
            validate_date_is_on_clinic_day(
                cleaned_data=dict(
                    appt_date=self.appt_date,
                    report_datetime=self.report_datetime,
                ),
                clinic_days=self.health_facility.clinic_days,
            )

        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        verbose_name = "Next Appointment"
        verbose_name_plural = "Next Appointments"
