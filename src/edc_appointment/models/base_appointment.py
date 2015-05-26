from django.db import models

from edc_base.model.models import BaseUuidModel

from ..choices import APPT_STATUS


class BaseAppointment (BaseUuidModel):
    """Base class for Appointments."""
    appt_datetime = models.DateTimeField(
        verbose_name=("Appointment date and time"),
        help_text="",
        db_index=True)
    # this is the original calculated edc_appointment datetime
    # which the user cannot change
    timepoint_datetime = models.DateTimeField(
        verbose_name=("Timepoint date and time"),
        help_text="calculated edc_appointment datetime. Do not change",
        null=True,
        editable=False)
    appt_status = models.CharField(
        verbose_name=("Status"),
        choices=APPT_STATUS,
        max_length=25,
        default='new',
        db_index=True)
    appt_reason = models.CharField(
        verbose_name=("Reason for edc_appointment"),
        max_length=25,
        help_text=("Reason for edc_appointment"),
        blank=True)
    contact_tel = models.CharField(
        verbose_name=("Contact Tel"),
        max_length=250,
        blank=True)
    comment = models.CharField(
        "Comment",
        max_length=250,
        blank=True)

    is_confirmed = models.BooleanField(default=False, editable=False)
    contact_count = models.IntegerField(default=0, editable=False)

    def get_report_datetime(self):
        return self.appt_datetime

    def is_new_appointment(self):
        """Returns True if this is a New edc_appointment and
        confirms choices tuple has \'new\'; as a option."""
        if 'new' not in [s[0] for s in APPT_STATUS]:
            raise TypeError(
                'Expected (\'new\', \'New\') as one tuple in the choices '
                'tuple APPT_STATUS. Got {0}'.format(APPT_STATUS))
        retval = False
        if self.appt_status.lower() == 'new':
            retval = True
        return retval

    class Meta:
        abstract = True
