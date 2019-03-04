from django.apps import apps as django_apps
from edc_utils import formatted_datetime

from .site_visit_schedules import site_visit_schedules


class OnScheduleError(Exception):
    pass


def get_offschedule_models(
    subject_identifier=None,
    report_datetime=None,
    subject_schedule_history_model_cls=None,
):
    """Returns a list of offschedule models, in label_lower format,
    for this subject and date.

    Subject status must be ON_SCHEDULE.

    See also, manager method `onschedules`.
    """
    offschedule_models = []
    SubjectScheduleHistory = (
        subject_schedule_history_model_cls
        or django_apps.get_model("edc_visit_schedule.SubjectScheduleHistory")
    )
    for onschedule_model_obj in SubjectScheduleHistory.objects.onschedules(
        subject_identifier=subject_identifier, report_datetime=report_datetime
    ):
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            onschedule_model=onschedule_model_obj._meta.label_lower
        )
        offschedule_models.append(schedule.offschedule_model)
    return offschedule_models


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
