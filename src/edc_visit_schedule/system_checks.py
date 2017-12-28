from django.core.checks import Warning

from .site_visit_schedules import site_visit_schedules


def visit_schedule_check(app_configs, **kwargs):
    errors = []

    if not site_visit_schedules.visit_schedules:
        errors.append(
            Warning(
                'No visit schedules have been registered!',
                id='edc_visit_schedule.001'))
    for visit_schedule in site_visit_schedules.visit_schedules.values():
        messages = visit_schedule.check()
        for message in messages:
            errors.append(
                Warning(message, id='edc_visit_schedule.002'))
    return errors
