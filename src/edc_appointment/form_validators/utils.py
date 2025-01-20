from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

from django.urls import reverse
from django.utils.html import format_html
from edc_dashboard.url_names import url_names
from edc_form_validators import INVALID_ERROR


def get_appointment_url(appointment_pk: str, subject_identifier: str) -> str:
    rev_url = reverse(
        "edc_appointment_admin:edc_appointment_appointment_change",
        args=(appointment_pk,),
    )
    rev_url = (
        f'{rev_url}?next={url_names.get("subject_dashboard_url")},'
        f"subject_identifier"
        f"&subject_identifier={subject_identifier}"
    )
    return rev_url


def validate_appt_datetime_unique(
    form_validator: Any,
    appointment: Any,
    appt_datetime: datetime,
    form_field: Optional[str] = None,
):
    """Assert one visit report per day"""
    if appt_datetime:
        form_field = form_field or "appt_datetime"
        appt_datetime_utc = appt_datetime.astimezone(ZoneInfo("UTC"))
        opts = {
            "subject_identifier": appointment.subject_identifier,
            "visit_schedule_name": appointment.visit_schedule_name,
            "schedule_name": appointment.schedule_name,
            "appt_datetime__date": appt_datetime_utc.date(),
        }
        other_appts = appointment.__class__.objects.filter(**opts).exclude(id=appointment.id)
        if other_appts.count() > 1:
            raise form_validator.raise_validation_error(
                {form_field: "An appointment already exists for this date (M)"},
                INVALID_ERROR,
            )
        elif other_appts.count() == 1:
            if appointment and other_appts[0].id != appointment.id:
                appointment_url = get_appointment_url(
                    (
                        appointment.id
                        if appointment.visit_code_sequence > 0
                        else other_appts[0].id
                    ),
                    appointment.subject_identifier,
                )
                if other_appts[0].visit_code_sequence == 0:
                    msg = format_html(
                        (
                            "This appointment conflicts with the scheduled appointment "
                            '{visit_code}.0. Consider editing <A href="{appointment_url}"> '
                            "this appointment</A> first."
                        ),
                        visit_code=other_appts[0].visit_code,
                        appointment_url=appointment_url,
                    )
                else:
                    phrase = (
                        "A scheduled"
                        if other_appts[0].visit_code_sequence == 0
                        else "An unscheduled"
                    )
                    msg = format_html(
                        "{phrase} appointment already exists for this date. "
                        'See <A title="Edit appointment" href="{appointment_url}">'
                        "appointment {visit_code}. {visit_code_sequence}</A>",
                        phrase=phrase,
                        appointment_url=appointment_url,
                        visit_code=other_appts[0].visit_code,
                        visit_code_sequence=other_appts[0].visit_code_sequence,
                    )
                raise form_validator.raise_validation_error(
                    {form_field: msg},
                    INVALID_ERROR,
                )
