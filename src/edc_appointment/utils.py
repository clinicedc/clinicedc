from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db import transaction
from django.db.models import ProtectedError

from .choices import DEFAULT_APPT_REASON_CHOICES
from .constants import CANCELLED_APPT, MISSED_APPT, SCHEDULED_APPT, UNSCHEDULED_APPT


def get_appt_reason_choices() -> tuple:
    """Returns a customized tuple of choices otherwise the default"""
    settings_attr = "EDC_APPOINTMENT_APPT_REASON_CHOICES"
    appt_reason_choices = getattr(settings, settings_attr, DEFAULT_APPT_REASON_CHOICES)
    required_keys = [choice[0] for choice in appt_reason_choices]
    for key in [SCHEDULED_APPT, UNSCHEDULED_APPT]:
        if key not in required_keys:
            raise ImproperlyConfigured(
                f"Invalid APPT_REASON_CHOICES. Missing key `{key}`. See {settings_attr}."
            )
    return appt_reason_choices


def cancelled_appointment(instance: Any):
    try:
        cancelled = instance.appt_status == CANCELLED_APPT
    except AttributeError as e:
        if "appt_status" not in str(e):
            raise
    else:
        if (
            cancelled
            and instance.visit_code_sequence > 0
            and "historical" not in instance._meta.label_lower
        ):
            try:
                subject_visit = instance.visit_model_cls().objects.get(appointment=instance)
            except ObjectDoesNotExist:
                instance.delete()
            else:
                with transaction.atomic():
                    try:
                        subject_visit.delete()
                    except ProtectedError:
                        pass


def missed_appointment(instance: Any):
    try:
        missed = instance.appt_timing == MISSED_APPT
    except AttributeError as e:
        if "appt_timing" not in str(e):
            raise
    else:
        if (
            missed
            and instance.visit_code_sequence == 0
            and "historical" not in instance._meta.label_lower
        ):
            try:
                instance.create_missed_visit_from_appointment()
            except AttributeError as e:
                if "create_missed_visit" not in str(e):
                    raise
