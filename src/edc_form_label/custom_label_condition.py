from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

if TYPE_CHECKING:
    from edc_appointment.models import Appointment


class CustomFormLabelError(Exception):
    pass


class CustomLabelCondition:
    appointment_model = "edc_appointment.appointment"

    def __init__(self, request=None, obj=None, model=None):
        self.request = request
        self.obj = obj
        self.model = model

    def check(self):
        """Override with custom logic.

        If True, form label will be customized. See`FormLabel`.
        """
        return

    def get_additional_options(self, request=None, obj=None, model=None):  # noqa: ARG002
        return {}

    @property
    def appointment(self) -> Appointment | None:
        """Returns the appointment instance for this request or None."""
        with contextlib.suppress(ObjectDoesNotExist):
            return django_apps.get_model(self.appointment_model).objects.get(
                pk=self.request.GET.get("appointment")
            )
        return None

    @property
    def previous_appointment(self) -> Appointment | None:
        """Returns the previous appointment for this request or None."""
        with contextlib.suppress(ObjectDoesNotExist):
            return self.appointment.previous_by_timepoint
        return None

    @property
    def previous_visit(self):
        """Returns the previous visit for this request or None.

        Requires attr `related_visit_model_cls`.
        """
        previous_visit = None
        if self.appointment:
            appointment = self.appointment
            while appointment.previous_by_timepoint:
                try:
                    previous_visit = self.model.related_visit_model_cls().objects.get(
                        appointment=appointment.previous_by_timepoint
                    )
                except ObjectDoesNotExist:
                    pass
                else:
                    break
                appointment = appointment.previous_by_timepoint
        return previous_visit

    @property
    def previous_obj(self):
        """Returns a model obj that is the first occurrence of a previous
        obj relative to this object's appointment.

        Override this method if not am EDC subject model / CRF.
        """
        previous_obj = None
        if self.previous_visit:
            with contextlib.suppress(ObjectDoesNotExist):
                previous_obj = self.model.objects.get(
                    **{f"{self.model.related_visit_model_attr()}": self.previous_visit}
                )
        return previous_obj
