from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.checks import Warning

from .exceptions import SiteVisitScheduleError
from .site_visit_schedules import site_visit_schedules

if TYPE_CHECKING:
    from .schedule import Schedule
    from .visit import Visit
    from .visit_schedule import VisitSchedule


def visit_schedule_check(app_configs, **kwargs):
    errors = []

    if not site_visit_schedules.visit_schedules:
        errors.append(
            Warning("No visit schedules have been registered!", id="edc_visit_schedule.001")
        )
    site_results = check_models()
    for key, results in site_results.items():
        for result in results:
            errors.append(Warning(result, id=f"edc_visit_schedule.{key}"))
    return errors


def check_models() -> dict[str, list]:
    if not site_visit_schedules.loaded:
        raise SiteVisitScheduleError("Registry is not loaded.")
    errors = {"visit_schedules": [], "schedules": [], "visits": []}
    for visit_schedule in site_visit_schedules.visit_schedules.values():
        errors["visit_schedules"].extend(check_visit_schedule_models(visit_schedule))
        for schedule in visit_schedule.schedules.values():
            errors["schedules"].extend(check_schedule_models(schedule))
            for visit in schedule.visits.values():
                errors["visits"].extend(check_visit_models(visit))
    return errors


def check_visit_schedule_models(visit_schedule: VisitSchedule) -> list[str]:
    warnings = []
    for model in ["death_report", "locator", "offstudy"]:
        try:
            getattr(visit_schedule, f"{model}_model_cls")
        except LookupError as e:
            warnings.append(f"{e} See visit schedule '{visit_schedule.name}'.")
    return warnings


def check_schedule_models(schedule: Schedule) -> list[str]:
    warnings = []
    for model in ["onschedule", "offschedule", "appointment"]:
        try:
            getattr(schedule, f"{model}_model_cls")
        except LookupError as e:
            warnings.append(f"{e} See visit schedule '{schedule.name}'.")
    return warnings


def check_visit_models(visit: Visit):
    warnings = []
    models = list(set([f.model for f in visit.all_crfs]))
    for model in models:
        try:
            django_apps.get_model(model)
        except LookupError as e:
            warnings.append(f"{e} Got Visit {visit.code} crf.model={model}.")
    models = list(set([f.model for f in visit.all_requisitions]))
    for model in models:
        try:
            django_apps.get_model(model)
        except LookupError as e:
            warnings.append(f"{e} Got Visit {visit.code} requisition.model={model}.")
    return warnings
