from django.core.checks import Warning

from .site_visit_schedules import site_visit_schedules


def visit_schedule_check(app_configs, **kwargs):
    errors = []

    if not site_visit_schedules.visit_schedules:
        errors.append(
            Warning(
                "No visit schedules have been registered!", id="edc_visit_schedule.001"
            )
        )
    site_results = site_visit_schedules.check()
    for key, results in site_results.items():
        for result in results:
            errors.append(Warning(result, id=f"edc_visit_schedule.{key}"))
    return errors
