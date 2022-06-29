from typing import Any

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db import transaction
from django.db.models import ProtectedError
from edc_visit_schedule.schedule.window import (
    ScheduledVisitWindowError,
    UnScheduledVisitWindowError,
)
from edc_visit_schedule.utils import is_baseline

from .choices import DEFAULT_APPT_REASON_CHOICES
from .constants import (
    CANCELLED_APPT,
    COMPLETE_APPT,
    INCOMPLETE_APPT,
    MISSED_APPT,
    NEW_APPT,
    SCHEDULED_APPT,
    UNSCHEDULED_APPT,
)
from .exceptions import AppointmentWindowError


def get_appointment_model_name() -> str:
    return "edc_appointment.appointment"


def get_appointment_model_cls() -> Any:
    return django_apps.get_model(get_appointment_model_name())


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
            and not instance.crf_metadata_keyed_exists
            and not instance.requisition_metadata_keyed_exists
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
                    else:
                        instance.delete()


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


def update_unscheduled_appointment_sequence(subject_identifier: str) -> None:
    visit_codes = [
        (obj.visit_schedule_name, obj.schedule_name, obj.visit_code)
        for obj in get_appointment_model_cls().objects.filter(
            subject_identifier=subject_identifier,
            appt_reason=UNSCHEDULED_APPT,
        )
    ]
    visit_codes = list(set(visit_codes))
    for visit_schedule_name, schedule_name, visit_code in visit_codes:
        for index, appointment in enumerate(
            get_appointment_model_cls()
            .objects.filter(
                subject_identifier=subject_identifier,
                visit_schedule_name=visit_schedule_name,
                schedule_name=schedule_name,
                appt_reason=UNSCHEDULED_APPT,
                visit_code=visit_code,
            )
            .order_by("appt_datetime")
        ):

            appointment.visit_code_sequence = index + 1
            appointment.save_base(update_fields=["visit_code_sequence"])
            subject_visit = appointment.visit
            if subject_visit:
                subject_visit.visit_code_sequence = index + 1
                subject_visit.save_base(update_fields=["visit_code_sequence"])
                for crf in subject_visit.get_crf_metadata():
                    crf.visit_code_sequence = index + 1
                    crf.save_base(update_fields=["visit_code_sequence"])
                for requisition in subject_visit.get_requisition_metadata():
                    requisition.visit_code_sequence = index + 1
                    requisition.save_base(update_fields=["visit_code_sequence"])


def insert_appointment_in_sequence(appointment: Any, proposed_visit_code_sequence: int) -> Any:

    return appointment


def delete_appointment_in_sequence(appointment: Any, from_post_delete=None) -> None:
    if not from_post_delete:
        with transaction.atomic():
            appointment.delete()
    update_unscheduled_appointment_sequence(subject_identifier=appointment.subject_identifier)
    return None


def raise_on_appt_datetime_not_in_window(appointment) -> None:
    if not is_baseline(instance=appointment):
        baseline_timepoint_datetime = appointment.__class__.objects.first_appointment(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
        ).timepoint_datetime
        try:
            appointment.schedule.datetime_in_window(
                dt=appointment.appt_datetime,
                timepoint_datetime=appointment.timepoint_datetime,
                visit_code=appointment.visit_code,
                visit_code_sequence=appointment.visit_code_sequence,
                baseline_timepoint_datetime=baseline_timepoint_datetime,
            )
        except ScheduledVisitWindowError as e:
            msg = str(e)
            msg.replace("Invalid datetime", "Invalid appointment datetime")
            raise AppointmentWindowError(msg)
        except UnScheduledVisitWindowError as e:
            msg = str(e)
            msg.replace("Invalid datetime", "Invalid appointment datetime")
            raise AppointmentWindowError(msg)


def update_appt_status(appointment, save=None):
    """Sets appt_status, and if save is True, calls save_base().

    This is useful if checking `appt_status` is correct
    relative to the visit tracking model and CRFs and
    requisitions
    """
    if appointment.appt_status == CANCELLED_APPT:
        pass
    elif not appointment.visit:
        appointment.appt_status = NEW_APPT
    else:
        if (
            appointment.crf_metadata_required_exists
            or appointment.requisition_metadata_required_exists
        ):
            appointment.appt_status = INCOMPLETE_APPT
        else:
            appointment.appt_status = COMPLETE_APPT
    if save:
        appointment.save_base(update_fields=["appt_status"])
        appointment.refresh_from_db()
    return appointment
