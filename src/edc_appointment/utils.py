from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Tuple

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
from .exceptions import AppointmentMissingValuesError, AppointmentWindowError

if TYPE_CHECKING:
    from .models import Appointment


def get_appointment_model_name() -> str:
    return "edc_appointment.appointment"


def get_appointment_model_cls() -> Appointment:
    return django_apps.get_model(get_appointment_model_name())


def get_appt_reason_choices() -> Tuple[str, ...]:
    """Returns a customized tuple of choices otherwise the default"""
    settings_attr = "EDC_APPOINTMENT_APPT_REASON_CHOICES"
    appt_reason_choices = getattr(settings, settings_attr, DEFAULT_APPT_REASON_CHOICES)
    required_keys = [choice[0] for choice in appt_reason_choices]
    for key in [SCHEDULED_APPT, UNSCHEDULED_APPT]:
        if key not in required_keys:
            raise ImproperlyConfigured(
                "Invalid value for EDC_APPOINTMENT_APPT_REASON_CHOICES. "
                f"Missing key `{key}`. See {settings_attr}."
            )
    return appt_reason_choices


def cancelled_appointment(appointment: Appointment) -> None:
    try:
        cancelled = appointment.appt_status == CANCELLED_APPT
    except AttributeError as e:
        if "appt_status" not in str(e):
            raise
    else:
        if (
            cancelled
            and appointment.visit_code_sequence > 0
            and "historical" not in appointment._meta.label_lower
            and not appointment.crf_metadata_keyed_exists
            and not appointment.requisition_metadata_keyed_exists
        ):
            try:
                related_visit = appointment.related_visit_model_cls().objects.get(
                    appointment=appointment
                )
            except ObjectDoesNotExist:
                appointment.delete()
            else:
                with transaction.atomic():
                    try:
                        related_visit.delete()
                    except ProtectedError:
                        pass
                    else:
                        appointment.delete()


def missed_appointment(appointment: Appointment) -> None:
    try:
        missed = appointment.appt_timing == MISSED_APPT
    except AttributeError as e:
        if "appt_timing" not in str(e):
            raise
    else:
        if (
            missed
            and appointment.visit_code_sequence == 0
            and "historical" not in appointment._meta.label_lower
        ):
            try:
                appointment.create_missed_visit_from_appointment()
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
            related_visit = appointment.related_visit
            if related_visit:
                related_visit.visit_code_sequence = index + 1
                related_visit.save_base(update_fields=["visit_code_sequence"])
                for crf in related_visit.get_crf_metadata():
                    crf.visit_code_sequence = index + 1
                    crf.save_base(update_fields=["visit_code_sequence"])
                for requisition in related_visit.get_requisition_metadata():
                    requisition.visit_code_sequence = index + 1
                    requisition.save_base(update_fields=["visit_code_sequence"])


def delete_appointment_in_sequence(appointment: Any, from_post_delete=None) -> None:
    if not from_post_delete:
        with transaction.atomic():
            appointment.delete()
    update_unscheduled_appointment_sequence(subject_identifier=appointment.subject_identifier)
    return None


def raise_on_appt_datetime_not_in_window(appointment: Appointment) -> None:
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
            msg.replace("Invalid datetime", "Invalid appointment datetime (S)")
            raise AppointmentWindowError(msg)
        except UnScheduledVisitWindowError as e:
            msg = str(e)
            msg.replace("Invalid datetime", "Invalid appointment datetime (U)")
            raise AppointmentWindowError(msg)


def update_appt_status(appointment: Appointment, save: bool | None = None):
    """Sets appt_status, and if save is True, calls save_base().

    This is useful if checking `appt_status` is correct
    relative to the visit tracking model and CRFs and
    requisitions
    """
    if appointment.appt_status == CANCELLED_APPT:
        pass
    elif not appointment.related_visit:
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


def get_previous_appointment(
    appointment: Appointment, include_interim: bool | None = None
) -> Appointment | None:
    """Returns the previous appointment model instance,
    or None, in this schedule.

    Keywords:
        * include_interim: include interim appointments
          (e.g. those where visit_code_sequence != 0)

    See also: `AppointmentMethodsModelMixin`
    """
    check_appointment_required_values_or_raise(appointment)
    opts: Dict[Any] = dict(
        subject_identifier=appointment.subject_identifier,
        visit_schedule_name=appointment.visit_schedule_name,
        schedule_name=appointment.schedule_name,
    )
    if include_interim:
        if appointment.visit_code_sequence != 0:
            opts.update(
                timepoint__lte=appointment.timepoint,
                visit_code_sequence__lt=appointment.visit_code_sequence,
            )
        else:
            opts.update(timepoint__lt=appointment.timepoint)
    elif not include_interim:
        opts.update(
            timepoint__lt=appointment.timepoint,
            visit_code_sequence=0,
        )

    appointments = (
        appointment.__class__.objects.filter(**opts)
        .exclude(id=appointment.id)
        .order_by("timepoint", "visit_code_sequence")
    )

    try:
        previous_appt = appointments.reverse()[0]
    except IndexError:
        previous_appt = None
    return previous_appt


def get_next_appointment(appointment: Appointment, include_interim=None) -> Appointment | None:
    """Returns the next appointment model instance,
    or None, in this schedule.

    Keywords:
        * include_interim: include interim appointments
          (e.g. those where visit_code_sequence != 0)

    See also: `AppointmentMethodsModelMixin`
    """
    next_appt: Appointment | None = None
    check_appointment_required_values_or_raise(appointment)
    if (
        not appointment.visit_schedule_name
        or not appointment.schedule_name
        or appointment.timepoint is None
    ):
        raise
    opts: Dict[Any] = dict(
        subject_identifier=appointment.subject_identifier,
        visit_schedule_name=appointment.visit_schedule_name,
        schedule_name=appointment.schedule_name,
    )
    if include_interim:
        break_on_next = False
        for obj in appointment.__class__.objects.filter(
            timepoint__gte=appointment.timepoint, **opts
        ).order_by("timepoint", "visit_code_sequence"):
            if break_on_next:
                next_appt = obj
                break
            if obj.id == appointment.id:
                break_on_next = True
    elif not include_interim:
        opts.update(
            timepoint__gt=appointment.timepoint,
            visit_code_sequence=0,
        )
        next_appt = (
            appointment.__class__.objects.filter(**opts)
            .exclude(id=appointment.id)
            .order_by("timepoint", "visit_code_sequence")
        ).first()
    return next_appt


def check_appointment_required_values_or_raise(appointment: Appointment) -> None:
    if (
        not appointment.visit_schedule_name
        or not appointment.schedule_name
        or not appointment.visit_code
        or appointment.visit_code_sequence is None
        or appointment.timepoint is None
    ):
        raise AppointmentMissingValuesError(
            f"Appointment instance is missing required values. See {appointment}."
        )
