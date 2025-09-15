from __future__ import annotations

import sys
from collections import Counter, defaultdict
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.checks import Error, Warning
from django.core.exceptions import ObjectDoesNotExist

from .site_visit_schedules import site_visit_schedules
from .utils import (
    check_models_in_visit_schedule,
    get_models_from_collection,
    get_proxy_models_from_collection,
    get_proxy_root_model,
)
from .visit import CrfCollection

if TYPE_CHECKING:
    from .visit import Visit


def visit_schedule_check(app_configs, **kwargs):
    errors = []
    if "migrate" not in sys.argv and "makemigrations" not in sys.argv:
        if not site_visit_schedules.visit_schedules:
            errors.append(
                Warning(
                    "No visit schedules have been registered!",
                    id="edc_visit_schedule.W001",
                )
            )
        site_results = check_models_in_visit_schedule()
        for category, results in site_results.items():
            for result in results:
                if category == "visit_schedules":
                    error_code = "E002"
                elif category == "schedules":
                    error_code = "E003"
                elif category == "visits":
                    error_code = "E004"
                else:
                    raise KeyError(f"Unexpected key. Got {category}.")

                errors.append(Warning(result, id=f"edc_visit_schedule.{error_code}"))
    return errors


def check_subject_schedule_history(app_configs, **kwargs) -> list:
    errors = []
    if "migrate" not in sys.argv and "makemigrations" not in sys.argv:
        subject_schedule_history_cls = django_apps.get_model(
            "edc_visit_schedule.subjectschedulehistory"
        )
        for obj in subject_schedule_history_cls.objects.all():
            try:
                obj.onschedule_obj
            except LookupError as e:
                errors.append(
                    Error(
                        "Invalid onschedule model referenced "
                        "in SubjectScheduleHistory. "
                        f"See {obj.onschedule_model} for {obj.subject_identifier} "
                        f"Got {e}",
                        id="edc_visit_schedule.E005",
                    )
                )
            except ObjectDoesNotExist:
                errors.append(
                    Error(
                        "Invalid onschedule model referenced in SubjectScheduleHistory. "
                        f"Got {obj.onschedule_model} for {obj.subject_identifier}",
                        id="edc_visit_schedule.E008",
                    )
                )
    return errors


def check_onschedule_exists_in_subject_schedule_history(app_configs, **kwargs) -> list:
    errors = []
    if "migrate" not in sys.argv and "makemigrations" not in sys.argv:
        subject_schedule_history_cls = django_apps.get_model(
            "edc_visit_schedule.subjectschedulehistory"
        )
        for visit_schedule in site_visit_schedules.visit_schedules.values():
            for schedule in visit_schedule.schedules.values():
                try:
                    onschedule_model_cls = schedule.onschedule_model_cls
                except LookupError:
                    pass
                else:
                    for obj in onschedule_model_cls.objects.all():
                        try:
                            subject_schedule_history_cls.objects.get(
                                subject_identifier=obj.subject_identifier,
                                onschedule_model=onschedule_model_cls._meta.label_lower,
                            )
                        except ObjectDoesNotExist:
                            errors.append(
                                Error(
                                    f"Onschedule instance not found in "
                                    "SubjectScheduleHistory. "
                                    f"See {obj.subject_identifier} "
                                    f"model {onschedule_model_cls._meta.label_lower}.",
                                    id="edc_visit_schedule.E009",
                                )
                            )
    return errors


def check_form_collections(app_configs, **kwargs):
    errors = []
    if "migrate" not in sys.argv and "makemigrations" not in sys.argv:
        for visit_schedule in site_visit_schedules.visit_schedules.values():
            for schedule in visit_schedule.schedules.values():
                for visit in schedule.visits.values():
                    for visit_crf_collection, visit_type in [
                        (visit.crfs, "Scheduled"),
                        (visit.crfs_unscheduled, "Unscheduled"),
                        (visit.crfs_missed, "Missed"),
                    ]:
                        if proxy_root_alongside_child_err := (
                            check_proxy_root_alongside_child(
                                visit=visit,
                                visit_crf_collection=visit_crf_collection,
                                visit_type=visit_type,
                            )
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
    all_models = get_models_from_collection(
        collection=visit_crf_collection
    ) + get_models_from_collection(collection=visit.crfs_prn)
    all_proxy_models = get_proxy_models_from_collection(
        collection=visit_crf_collection
    ) + get_proxy_models_from_collection(collection=visit.crfs_prn)

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
            id="edc_visit_schedule.E006",
        )
    return None


def check_multiple_proxies_same_proxy_root(
    visit: Visit,
    visit_crf_collection: CrfCollection,
    visit_type: str,
) -> Error | None:
    # Find all proxy models, and map from their 'proxy root' models
    all_proxy_models = get_proxy_models_from_collection(
        collection=visit_crf_collection
    ) + get_proxy_models_from_collection(collection=visit.crfs_prn)
    proxy_root_to_child_proxies: defaultdict[str, list[str]] = defaultdict(list)
    for proxy_model in all_proxy_models:
        child_proxy_model_str = proxy_model._meta.label.lower()
        proxy_root_model_str = get_proxy_root_model(proxy_model)._meta.label.lower()
        proxy_root_to_child_proxies[proxy_root_model_str].append(child_proxy_model_str)

    # Find proxy models declared as sharing a proxy root
    proxies_sharing_roots = get_proxy_models_from_collection(
        collection=CrfCollection(*[f for f in visit_crf_collection if f.shares_proxy_root])
    ) + get_proxy_models_from_collection(
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
            id="edc_visit_schedule.E007",
        )
    return None
