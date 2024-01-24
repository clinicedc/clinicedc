from __future__ import annotations

from collections import Counter, defaultdict
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.checks import Error, Warning
from django.db import models

from .exceptions import SiteVisitScheduleError
from .site_visit_schedules import site_visit_schedules
from .visit import CrfCollection

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


def check_form_collections(app_configs, **kwargs):
    errors = []
    for visit_schedule in site_visit_schedules.visit_schedules.values():
        for schedule in visit_schedule.schedules.values():
            for visit in schedule.visits.values():
                for visit_crf_collection, visit_type in [
                    (visit.crfs, "Scheduled"),
                    (visit.crfs_unscheduled, "Unscheduled"),
                    (visit.crfs_missed, "Missed"),
                ]:
                    if proxy_root_alongside_child_err := check_proxy_root_alongside_child(
                        visit=visit,
                        visit_crf_collection=visit_crf_collection,
                        visit_type=visit_type,
                    ):
                        errors.append(proxy_root_alongside_child_err)

                    if same_proxy_root_err := check_multiple_proxies_same_proxy_root(
                        visit=visit,
                        visit_crf_collection=visit_crf_collection,
                        visit_type=visit_type,
                    ):
                        errors.append(same_proxy_root_err)

    return errors


def check_proxy_root_alongside_child(
    visit: Visit,
    visit_crf_collection: CrfCollection,
    visit_type: str,
) -> Error | None:
    all_models = get_models(collection=visit_crf_collection) + get_models(
        collection=visit.crfs_prn
    )
    all_proxy_models = get_proxy_models(collection=visit_crf_collection) + get_proxy_models(
        collection=visit.crfs_prn
    )

    if child_proxies_alongside_proxy_roots := [
        m for m in all_proxy_models if get_proxy_root_model(m) in all_models
    ]:
        proxy_root_child_pairs = [
            (
                f"proxy_root_model={get_proxy_root_model(proxy)._meta.label_lower}",
                f"proxy_model={proxy._meta.label_lower}",
            )
            for proxy in child_proxies_alongside_proxy_roots
        ]
        return Error(
            "Proxy root model class appears alongside associated child "
            "proxy for a visit. "
            f"Got '{visit}' '{visit_type}' visit Crf collection. "
            f"Proxy root:child models: {proxy_root_child_pairs=}",
            id="edc_visit_schedule.003",
        )


def check_multiple_proxies_same_proxy_root(
    visit: Visit,
    visit_crf_collection: CrfCollection,
    visit_type: str,
) -> Error | None:
    # Find all proxy models, and map from their 'proxy root' models
    all_proxy_models = get_proxy_models(collection=visit_crf_collection) + get_proxy_models(
        collection=visit.crfs_prn
    )
    proxy_root_to_child_proxies: defaultdict[str, list[str]] = defaultdict(list)
    for proxy_model in all_proxy_models:
        child_proxy_model_str = proxy_model._meta.label.lower()
        proxy_root_model_str = get_proxy_root_model(proxy_model)._meta.label.lower()
        proxy_root_to_child_proxies[proxy_root_model_str].append(child_proxy_model_str)

    # Find proxy models declared as sharing a proxy root
    proxies_sharing_roots = get_proxy_models(
        collection=CrfCollection(*[f for f in visit_crf_collection if f.shares_proxy_root])
    ) + get_proxy_models(
        collection=CrfCollection(*[f for f in visit.crfs_prn if f.shares_proxy_root])
    )
    proxies_sharing_roots_counter = Counter(
        [m._meta.label.lower() for m in proxies_sharing_roots]
    )

    # Filter out valid models/prepare error list
    for proxy_root in list(proxy_root_to_child_proxies):
        proxies_counter = Counter(proxy_root_to_child_proxies[proxy_root])
        if proxies_counter & proxies_sharing_roots_counter == proxies_counter:
            # OK if proxies counter reflects ALL defined proxy shared roots
            del proxy_root_to_child_proxies[proxy_root]
        elif len(proxies_counter) == 1 and next(iter(proxies_counter.values())) <= 2:
            # OK for a single proxy to be defined in two places (CRFs collection + PRNs)
            del proxy_root_to_child_proxies[proxy_root]
        else:
            proxy_root_to_child_proxies[proxy_root].sort()

    if proxy_root_to_child_proxies:
        return Error(
            "Multiple proxies with same proxy root model appear for "
            "a visit. If this is intentional, consider using "
            "`shares_proxy_root` argument when defining Crf. "
            f"Got '{visit}' '{visit_type}' visit Crf collection. "
            f"Proxy root/child models: {dict(proxy_root_to_child_proxies)}",
            id="edc_visit_schedule.004",
        )


def get_models(collection: CrfCollection) -> list[models.Model]:
    return [f.model_cls for f in collection]


def get_proxy_models(collection: CrfCollection) -> list[models.Model]:
    return [f.model_cls for f in collection if f.model_cls._meta.proxy]


def get_proxy_root_model(proxy_model: models.Model) -> models.Model | None:
    """Returns proxy's root (concrete) model if `proxy_model` is a
    proxy model, else returns None.
    """
    if proxy_model._meta.proxy:
        return proxy_model._meta.concrete_model
