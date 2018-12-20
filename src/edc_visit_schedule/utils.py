from django.apps import apps as django_apps

from .site_visit_schedules import site_visit_schedules


def get_offschedule_models(subject_identifier=None, report_datetime=None,
                           subject_schedule_history_model_cls=None):
    """Returns a list of offschedule models, in label_lower format,
    for this subject and date.

    Subject status must be ON_SCHEDULE.

    See also, manager method `onschedules`.
    """
    offschedule_models = []
    SubjectScheduleHistory = subject_schedule_history_model_cls or django_apps.get_model(
        'edc_visit_schedule.SubjectScheduleHistory')
    for onschedule_model_obj in SubjectScheduleHistory.objects.onschedules(
            subject_identifier=subject_identifier,
            report_datetime=report_datetime):
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            onschedule_model=onschedule_model_obj._meta.label_lower)
        offschedule_models.append(schedule.offschedule_model)
    return offschedule_models
