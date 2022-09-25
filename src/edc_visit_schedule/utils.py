from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional

from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from edc_utils import formatted_datetime

from .exceptions import OffScheduleError, OnScheduleError
from .site_visit_schedules import SiteVisitScheduleError, site_visit_schedules


class VisitScheduleBaselineError(Exception):
    pass


class Baseline:
    def __init__(
        self,
        instance: Optional[Any] = None,
        timepoint: Optional[Decimal] = None,
        visit_code_sequence: Optional[int] = None,
        visit_schedule_name: Optional[str] = None,
        schedule_name: Optional[str] = None,
    ):
        if instance:
            try:
                instance = instance.appointment
            except AttributeError:
                try:
                    instance = instance.subject_visit.appointment
                except AttributeError:
                    pass
            self.visit_schedule_name = instance.visit_schedule_name
            self.schedule_name = instance.schedule_name
            self.visit_code_sequence = instance.visit_code_sequence
            self.timepoint = instance.timepoint
        else:
            self.visit_schedule_name = visit_schedule_name
            self.schedule_name = schedule_name
            self.visit_code_sequence = visit_code_sequence
            self.timepoint = timepoint
            if self.timepoint is None:
                raise VisitScheduleBaselineError("timpoint may not be None")
        if not any([x == self.timepoint for x in self.timepoints.values()]):
            raise VisitScheduleBaselineError(
                f"Unknown timepoint. For schedule {self.visit_schedule}.{self.schedule}. "
                f"Got {self.timepoint} not in {self.timepoints}"
            )
        self.value: bool = (
            self.timepoint == self.baseline_timepoint and self.visit_code_sequence == 0
        )

    @property
    def visit_schedule(self):
        self.have_required_attrs_or_raise()
        try:
            visit_schedule = site_visit_schedules.get_visit_schedule(self.visit_schedule_name)
        except SiteVisitScheduleError as e:
            raise VisitScheduleBaselineError(str(e))
        return visit_schedule

    @property
    def schedule(self):
        try:
            schedule = self.visit_schedule.schedules.get(self.schedule_name)
        except SiteVisitScheduleError as e:
            raise VisitScheduleBaselineError(str(e))
        return schedule

    @property
    def baseline_timepoint(self):
        """Returns a decimal that is the first timepoint in this schedule"""
        return self.schedule.visits.first.timepoint

    @property
    def timepoints(self):
        return self.schedule.visits.timepoints

    def have_required_attrs_or_raise(self):
        data = {
            k: getattr(self, k, None) is None
            for k in [
                "visit_schedule_name",
                "schedule_name",
                "visit_code_sequence",
                "timepoint",
            ]
        }

        if any(data.values()):
            raise VisitScheduleBaselineError(
                "Missing value(s). Unable to determine if baseline. "
                f"Got `None` for {[k for k, v in data.items() if v is True]}."
            )


def is_baseline(
    instance: Optional[Any] = None,
    timepoint: Optional[Decimal] = None,
    visit_code_sequence: Optional[int] = None,
    visit_schedule_name: Optional[str] = None,
    schedule_name: Optional[str] = None,
) -> bool:
    return Baseline(
        instance=instance,
        timepoint=timepoint,
        visit_code_sequence=visit_code_sequence,
        visit_schedule_name=visit_schedule_name,
        schedule_name=schedule_name,
    ).value


def raise_if_baseline(subject_visit) -> None:
    if subject_visit and is_baseline(instance=subject_visit):
        raise forms.ValidationError("This form is not available for completion at baseline.")


def raise_if_not_baseline(subject_visit) -> None:
    if subject_visit and not is_baseline(instance=subject_visit):
        raise forms.ValidationError("This form is only available for completion at baseline.")


def get_onschedule_models(
    subject_identifier: str = None, report_datetime: datetime = None
) -> List[str]:
    """Returns a list of onschedule models, in label_lower format,
    for this subject and date.
    """
    onschedule_models = []
    subject_schedule_history_model_cls = django_apps.get_model(
        "edc_visit_schedule.SubjectScheduleHistory"
    )
    for onschedule_model_obj in subject_schedule_history_model_cls.objects.onschedules(
        subject_identifier=subject_identifier, report_datetime=report_datetime
    ):
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            onschedule_model=onschedule_model_obj._meta.label_lower
        )
        onschedule_models.append(schedule.onschedule_model)
    return onschedule_models


def get_offschedule_models(subject_identifier=None, report_datetime=None):
    """Returns a list of offschedule models, in label_lower format,
    for this subject and date.

    Subject status must be ON_SCHEDULE.

    See also, manager method `onschedules`.
    """
    offschedule_models = []
    subject_schedule_history_model_cls = django_apps.get_model(
        "edc_visit_schedule.SubjectScheduleHistory"
    )
    onschedule_models = subject_schedule_history_model_cls.objects.onschedules(
        subject_identifier=subject_identifier, report_datetime=report_datetime
    )
    for onschedule_model_obj in onschedule_models:
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            onschedule_model=onschedule_model_obj._meta.label_lower
        )
        offschedule_models.append(schedule.offschedule_model)
    return offschedule_models


def get_subject_schedule_cls(model, visit_schedule, schedule):
    try:
        subject_schedule_cls = model.subject_schedule_cls(
            visit_schedule=visit_schedule, schedule=schedule
        )
    except AttributeError as e:
        if "subject_schedule_cls" in str(e):
            raise AttributeError(
                f"{e}. Perhaps model `{model._meta.label_lower}` should be declared "
                f"with `CrfScheduleModelMixin`?"
            )
        else:
            raise
    return subject_schedule_cls


def off_schedule_or_raise(
    subject_identifier=None,
    report_datetime=None,
    visit_schedule_name=None,
    schedule_name=None,
):
    """Returns True if subject is on the given schedule
    on this date.
    """
    visit_schedule = site_visit_schedules.get_visit_schedule(
        visit_schedule_name=visit_schedule_name
    )
    schedule = visit_schedule.schedules.get(schedule_name)
    if schedule.is_onschedule(
        subject_identifier=subject_identifier, report_datetime=report_datetime
    ):
        raise OnScheduleError(
            f"Not allowed. Subject {subject_identifier} is on schedule "
            f"{visit_schedule.verbose_name}.{schedule_name} on "
            f"{formatted_datetime(report_datetime)}. "
            f"See model '{schedule.offschedule_model_cls().verbose_name}'"
        )


def off_all_schedules_or_raise(subject_identifier: str = None):
    """Raises an exception if subject is still on any schedule."""
    for visit_schedule in site_visit_schedules.get_visit_schedules().values():
        for schedule in visit_schedule.schedules.values():
            try:
                with transaction.atomic():
                    schedule.onschedule_model_cls.objects.get(
                        subject_identifier=subject_identifier
                    )
            except ObjectDoesNotExist:
                pass
            else:
                try:
                    with transaction.atomic():
                        schedule.offschedule_model_cls.objects.get(
                            subject_identifier=subject_identifier
                        )
                except ObjectDoesNotExist:
                    model_name = schedule.offschedule_model_cls()._meta.verbose_name.title()
                    raise OffScheduleError(
                        f"Subject cannot be taken off study. Subject is still on a "
                        f"schedule. Got schedule '{visit_schedule.name}.{schedule.name}. "
                        f"Complete the offschedule form `{model_name}` first. "
                        f"Subject identifier='{subject_identifier}', "
                    )
    return True


def offstudy_datetime_after_all_offschedule_datetimes(
    subject_identifier: str = None,
    offstudy_datetime: datetime = None,
    exception_cls=None,
):
    exception_cls = exception_cls or forms.ValidationError
    for visit_schedule in site_visit_schedules.get_visit_schedules().values():
        for schedule in visit_schedule.schedules.values():
            try:
                schedule.onschedule_model_cls.objects.get(
                    subject_identifier=subject_identifier
                )
            except ObjectDoesNotExist:
                pass
            else:
                try:
                    offschedule_obj = schedule.offschedule_model_cls.objects.get(
                        subject_identifier=subject_identifier,
                        offschedule_datetime__gt=offstudy_datetime,
                    )
                except ObjectDoesNotExist:
                    pass
                else:
                    offschedule_datetime = formatted_datetime(
                        offschedule_obj.offschedule_datetime
                    )
                    raise exception_cls(
                        "`Offstudy` datetime cannot be before any `offschedule` datetime. "
                        f"Got {subject_identifier} went off schedule "
                        f"`{visit_schedule.name}.{schedule.name}` on "
                        f"{offschedule_datetime}."
                    )


def report_datetime_within_onschedule_offschedule_datetimes(
    subject_identifier: str = None,
    report_datetime: datetime = None,
    visit_schedule_name: str = None,
    schedule_name: str = None,
    exception_cls=None,
):
    exception_cls = exception_cls or forms.ValidationError
    visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name)
    schedule = visit_schedule.schedules.get(schedule_name)
    try:
        onschedule_obj = schedule.onschedule_model_cls.objects.get(
            subject_identifier=subject_identifier
        )
    except ObjectDoesNotExist:
        raise OnScheduleError(
            f"Subject is not on schedule. {visit_schedule_name}.{schedule_name}. "
            f"Got {subject_identifier}"
        )
    try:
        offschedule_obj = schedule.offschedule_model_cls.objects.get(
            subject_identifier=subject_identifier,
            offschedule_datetime__lte=report_datetime,
        )
    except ObjectDoesNotExist:
        offschedule_obj = None
        offschedule_datetime = report_datetime
    else:
        offschedule_datetime = offschedule_obj.offschedule_datetime
    if not (onschedule_obj.onschedule_datetime <= report_datetime <= offschedule_datetime):
        onschedule_datetime = formatted_datetime(onschedule_obj.onschedule_datetime)
        if offschedule_obj:
            offschedule_datetime = formatted_datetime(offschedule_obj.offschedule_datetime)
            error_msg = (
                "Invalid report datetime. Expected a datetime between "
                f"{onschedule_datetime} and {offschedule_datetime}. "
                "See onschedule and offschedule."
            )
        else:
            error_msg = (
                "Invalid report datetime. Expected a datetime on or after "
                f"{onschedule_datetime}. See onschedule."
            )
        raise exception_cls(error_msg)


def get_onschedule_model_instance(
    subject_identifier: str,
    reference_datetime: datetime,
    visit_schedule_name: str,
    schedule_name: str,
) -> Any:
    """Returns the onschedule model instance"""
    schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name).schedules.get(
        schedule_name
    )
    model_cls = django_apps.get_model(schedule.onschedule_model)
    try:
        onschedule_obj = model_cls.objects.get(
            subject_identifier=subject_identifier,
            onschedule_datetime__lte=reference_datetime,
        )
    except ObjectDoesNotExist as e:
        dte_as_str = formatted_datetime(reference_datetime)
        raise OffScheduleError(
            "Subject is not on a schedule. Using subject_identifier="
            f"`{subject_identifier}` and appt_datetime=`{dte_as_str}`. Got {e}"
        )
    return onschedule_obj
