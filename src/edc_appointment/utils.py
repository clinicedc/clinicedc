from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Tuple

from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db import transaction
from django.db.models import ProtectedError
from edc_constants.constants import CLINIC
from edc_utils import convert_php_dateformat
from edc_visit_schedule.schedule.window import (
    ScheduledVisitWindowError,
    UnScheduledVisitWindowError,
)
from edc_visit_schedule.utils import get_default_max_visit_window_gap, is_baseline

from .choices import APPT_TYPE, DEFAULT_APPT_REASON_CHOICES
from .constants import (
    CANCELLED_APPT,
    COMPLETE_APPT,
    INCOMPLETE_APPT,
    MISSED_APPT,
    NEW_APPT,
    SCHEDULED_APPT,
    UNSCHEDULED_APPT,
)
from .exceptions import (
    AppointmentBaselineError,
    AppointmentMissingValuesError,
    AppointmentWindowError,
    UnscheduledAppointmentError,
)

if TYPE_CHECKING:
    from .models import Appointment


class AppointmentDateWindowPeriodGapError(Exception):
    pass


def get_appointment_model_name() -> str:
    return "edc_appointment.appointment"


def get_appointment_model_cls() -> Appointment:
    return django_apps.get_model(get_appointment_model_name())


def get_allow_missed_unscheduled_appts() -> bool:
    """Returns value of settings attr or False"""
    return getattr(settings, "EDC_VISIT_TRACKING_ALLOW_MISSED_UNSCHEDULED", False)


def raise_on_appt_may_not_be_missed(
    appointment: Appointment = None,
    appt_timing: str | None = None,
):
    if appointment.id:
        appt_timing = appt_timing or appointment.appt_timing
        if appt_timing and appt_timing == MISSED_APPT and is_baseline(instance=appointment):
            raise AppointmentBaselineError(
                "Invalid. A baseline appointment may not be reported as missed"
            )
        if (
            appointment.visit_code_sequence is not None
            and appt_timing
            and appointment.visit_code_sequence > 0
            and appt_timing == MISSED_APPT
            and not get_allow_missed_unscheduled_appts()
        ):
            raise UnscheduledAppointmentError(
                "Invalid. An unscheduled appointment may not be reported as missed."
                "Try to cancel the appointment instead. "
            )


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


def get_appt_type_choices() -> Tuple[str, ...]:
    """Returns a customized tuple of choices otherwise the default"""
    settings_attr = "EDC_APPOINTMENT_APPT_TYPE_CHOICES"
    appt_type_choices = getattr(settings, settings_attr, APPT_TYPE)
    if get_appt_type_default() and not [
        choice[0] for choice in appt_type_choices if get_appt_type_default() == choice[0]
    ]:
        raise ImproperlyConfigured(
            "Missing default value in EDC_APPOINTMENT_APPT_TYPE_CHOICES. "
            f"Missing key `{get_appt_type_default()}`. See {settings_attr} and "
            "EDC_APPOINTMENT_APPT_TYPE_DEFAULT."
        )
    return appt_type_choices


def get_appt_type_default():
    settings_attr = "EDC_APPOINTMENT_APPT_TYPE_DEFAULT"
    return getattr(settings, settings_attr, CLINIC)


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


def raise_on_appt_datetime_not_in_window(
    appointment: Appointment,
    appt_datetime: datetime | None = None,
    baseline_timepoint_datetime: datetime | None = None,
) -> None:
    if appointment.appt_status != CANCELLED_APPT and not is_baseline(instance=appointment):
        baseline_timepoint_datetime = baseline_timepoint_datetime or (
            baseline_timepoint_datetime
            or appointment.__class__.objects.first_appointment(
                subject_identifier=appointment.subject_identifier,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
            ).timepoint_datetime
        )
        try:
            appointment.schedule.datetime_in_window(
                dt=appt_datetime or appointment.appt_datetime,
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


def get_window_gap_days(appointment) -> int:
    """Return the number of days betwen this visit's upper and the
    next visit's lower.

    See get_default_max_visit_window_gap and settings attr.
    """
    if not appointment.next:
        gap_days = 0
    else:
        gap_days = abs(
            (appointment.timepoint_datetime + appointment.visit.rupper)
            - (appointment.next.timepoint_datetime - appointment.next.visit.rlower)
        ).days
    return gap_days


def appt_datetime_in_gap(appointment: Appointment, suggested_appt_datetime: datetime) -> bool:
    """Return True if datetime falls in a gap between this and the
    next appointment window.
    """
    in_gap = False
    if get_window_gap_days(appointment) > 0:
        next_lower_datetime = (
            appointment.next.timepoint_datetime - appointment.next.visit.rlower
        )
        upper_datetime = appointment.timepoint_datetime + appointment.visit.rupper
        if upper_datetime < suggested_appt_datetime < next_lower_datetime:
            in_gap = True
    return in_gap


def get_max_window_gap_to_lower(appointment) -> int:
    if (
        appointment.visit.max_window_gap_to_lower is not None
        and appointment.visit.max_window_gap_to_lower < get_default_max_visit_window_gap()
    ):
        max_gap = appointment.visit.max_window_gap_to_lower
    else:
        max_gap = get_default_max_visit_window_gap()
    return max_gap


def appt_datetime_in_next_window_adjusted_for_gap(
    appointment: Appointment, suggested_appt_datetime: datetime
) -> bool:
    """Returns True if `suggest_datetime` falls between the
    NEXT appointment's lower and upper window period datetime after
    adding gap_days to the lower datetime.
    """
    in_window = False
    gap_days = get_window_gap_days(appointment)
    max_gap = get_max_window_gap_to_lower(appointment)
    gap_days = max_gap if gap_days > max_gap else gap_days
    if gap_days > 0:
        next_lower_datetime = (
            appointment.next.timepoint_datetime
            - appointment.next.visit.rlower
            - relativedelta(days=gap_days)
        )
        next_upper_datetime = (
            appointment.next.timepoint_datetime + appointment.next.visit.rupper
        )
        if next_lower_datetime <= suggested_appt_datetime <= next_upper_datetime:
            in_window = True
    return in_window


def get_appointment_by_datetime(
    suggested_appt_datetime: datetime,
    subject_identifier: str,
    visit_schedule_name: str,
    schedule_name: str,
    raise_if_in_gap: bool | None = None,
) -> Appointment | None:
    """Returns an appointment where the suggested datetime falls
    within the window period.

    * Returns None if no appointment is found.
    * Raises an exception if there is a gap between upper and lower
      boundaries and the date falls within the gap.
    """
    appointment = None
    raise_if_in_gap = True if raise_if_in_gap is None else raise_if_in_gap
    appointments = (
        django_apps.get_model("edc_appointment.appointment")
        .objects.filter(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
            visit_code_sequence=0,
        )
        .order_by("timepoint_datetime")
    )
    for appointment in appointments:
        if appointment.appt_status == CANCELLED_APPT or is_baseline(appointment):
            continue
        try:
            raise_on_appt_datetime_not_in_window(
                appointment, appt_datetime=suggested_appt_datetime
            )
        except AppointmentWindowError:
            in_gap = appt_datetime_in_gap(appointment, suggested_appt_datetime)
            in_next_window_adjusted = appt_datetime_in_next_window_adjusted_for_gap(
                appointment, suggested_appt_datetime
            )
            if in_gap and raise_if_in_gap:
                dt = suggested_appt_datetime.strftime(
                    convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                )
                raise AppointmentDateWindowPeriodGapError(
                    f"Date falls in a `window period gap` between {appointment.visit_code} "
                    f"and {appointment.next.visit_code}. Got {dt}."
                )
            elif (
                in_gap
                and in_next_window_adjusted
                and appointment.next.visit.add_window_gap_to_lower
            ):
                appointment = appointment.next
                break
            elif (
                in_gap
                and not in_next_window_adjusted
                and appointment.next.visit.add_window_gap_to_lower
            ):
                appointment = None
                break
            else:
                appointment = appointment.next
        else:
            break
    return appointment
