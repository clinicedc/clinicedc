from __future__ import annotations

from django.db import models
from django.db.models import PROTECT
from django.utils.translation import gettext_lazy as _
from edc_facility.utils import get_health_facility_model
from edc_visit_schedule.models import VisitSchedule


class NextAppointmentCrfModelMixin(models.Model):
    health_facility = models.ForeignKey(
        get_health_facility_model(),
        on_delete=PROTECT,
        null=True,
        blank=True,
    )

    appt_date = models.DateField(
        verbose_name=_("Next scheduled routine/facility appointment"),
        null=True,
        blank=False,
        help_text=_("Should fall on an Integrated clinic day"),
    )

    info_source = models.ForeignKey(
        "edc_appointment.infosources",
        verbose_name=_("What is the source of this appointment date"),
        max_length=15,
        on_delete=PROTECT,
        null=True,
        blank=False,
    )

    # named this way to not conflict with property `visit_schedule`
    # see also edc-crf
    visitschedule = models.ForeignKey(
        VisitSchedule,
        on_delete=PROTECT,
        verbose_name=_("Which study visit code is closest to this appointment date"),
        max_length=15,
        null=True,
        blank=False,
        help_text=_(
            "Click SAVE to let the EDC suggest. Once selected, interim appointments will "
            "be flagged as not required/missed."
        ),
    )

    allow_create_interim = models.BooleanField(
        verbose_name=_("Override date check?"),
        default=False,
        help_text=(
            "Override date check to allow the EDC to create an interim appointment if the "
            "date is within window period of the current appointment."
        ),
    )

    class Meta:
        abstract = True
        verbose_name = "Next Appointment"
        verbose_name_plural = "Next Appointments"
