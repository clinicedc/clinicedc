from django.db import models

from edc.device.sync.models import BaseSyncUuidModel
from edc_constants.constants import NEW_APPT

from ..choices import APPT_STATUS

try:
    from edc.device.dispatch.models import BaseDispatchSyncUuidModel

    class BaseBaseAppointment(BaseDispatchSyncUuidModel):
        class Meta:
            abstract = True

except ImportError:

    class BaseBaseAppointment(models.Model):
        class Meta:
            abstract = True


class BaseAppointment (BaseBaseAppointment, BaseSyncUuidModel):
    """Base class for Appointments."""

    appt_datetime = models.DateTimeField(
        verbose_name=("Appointment date and time"),
        help_text="",
        db_index=True)

    # this is the original calculated appointment datetime
    # which the user cannot change
    timepoint_datetime = models.DateTimeField(
        verbose_name=("Timepoint date and time"),
        help_text="calculated appointment datetime. Do not change",
        null=True,
        editable=False)

    appt_status = models.CharField(
        verbose_name=("Status"),
        choices=APPT_STATUS,
        max_length=25,
        default=NEW_APPT,
        db_index=True)

    appt_reason = models.CharField(
        verbose_name=("Reason for appointment"),
        max_length=25,
        help_text=("Reason for appointment"),
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
        """Returns True if this is a New appointment and confirms choices
        tuple has \'new\'; as a option."""
        if NEW_APPT not in [s[0] for s in APPT_STATUS]:
            raise TypeError(
                'Expected (\'new\', \'New\') as one tuple in the choices tuple '
                'APPT_STATUS. Got {0}'.format(APPT_STATUS))
        retval = False
        if self.appt_status == NEW_APPT:
            retval = True
        return retval

    class Meta:
        abstract = True
