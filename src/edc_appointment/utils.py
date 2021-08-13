from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .constants import SCHEDULED_APPT, UNSCHEDULED_APPT


def get_appt_reason_choices(default_choices: tuple) -> tuple:
    settings_attr = "EDC_APPOINTMENT_APPT_REASON_CHOICES"
    appt_reason_choices = getattr(settings, settings_attr, default_choices)
    required_keys = [choice[0] for choice in appt_reason_choices]
    for key in [SCHEDULED_APPT, UNSCHEDULED_APPT]:
        if key not in required_keys:
            raise ImproperlyConfigured(
                f"Invalid APPT_REASON_CHOICES. Missing key `{key}`. See {settings_attr}."
            )
    return appt_reason_choices
