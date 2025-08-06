from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db import models

from ..constants import CANCELLED_APPT
from ..exceptions import AppointmentWindowError
from ..utils import raise_on_appt_datetime_not_in_window

if TYPE_CHECKING:
    from ..models import Appointment


class WindowPeriodModelMixin(models.Model):
    """A model mixin declared with the Appointment model to managed
    window period calculations for appt_datetime.
    """

    window_period_checks_enabled: bool = True

    def save(self: Any, *args, **kwargs) -> None:
        if not kwargs.get("update_fields", None):
            self.raise_on_appt_datetime_not_in_window()
        super().save(*args, **kwargs)

    def raise_on_appt_datetime_not_in_window(self: Appointment) -> None:
        if (
            self.id
            and self.appt_status != CANCELLED_APPT
            and self.appt_datetime
            and self.timepoint_datetime
        ):
            if not self.ignore_window_period:
                try:
                    raise_on_appt_datetime_not_in_window(self)
                except AppointmentWindowError as e:
                    msg = f"{e} Perhaps catch this in the form"
                    raise AppointmentWindowError(msg)

    class Meta:
        abstract = True
