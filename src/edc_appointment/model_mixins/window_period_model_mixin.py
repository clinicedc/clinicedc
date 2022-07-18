from typing import Any

from django.db import models

from ..exceptions import AppointmentWindowError
from ..utils import raise_on_appt_datetime_not_in_window


class WindowPeriodModelMixin(models.Model):
    """A model mixin declared with the Appointment model to managed
    window period calculations for appt_datetime.
    """

    window_period_checks_enabled = True

    def save(self: Any, *args, **kwargs) -> None:
        if not kwargs.get("update_fields", None):
            if self.id and self.appt_datetime and self.timepoint_datetime:
                if not self.ignore_window_period:
                    try:
                        raise_on_appt_datetime_not_in_window(self)
                    except AppointmentWindowError as e:
                        msg = f"{e} Perhaps catch this in the form"
                        raise AppointmentWindowError(msg)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
