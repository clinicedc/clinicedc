from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from django.core.checks import Error, Warning
from django.db import models

from .site_visit_schedules import site_visit_schedules
from .utils import get_duplicates
from .visit import CrfCollection

if TYPE_CHECKING:
    from .visit import Visit


def visit_schedule_check(app_configs, **kwargs):
    errors = []

    if not site_visit_schedules.visit_schedules:
        errors.append(
            Warning("No visit schedules have been registered!", id="edc_visit_schedule.001")
        )
    site_results = site_visit_schedules.check()
    for key, results in site_results.items():
        for result in results:
            errors.append(Warning(result, id=f"edc_visit_schedule.{key}"))
    return errors


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
                    if duplicate_required_models_err := check_duplicate_required_models(
                        visit=visit,
                        visit_crf_collection=visit_crf_collection,
                        visit_type=visit_type,
                    ):
                        errors.append(duplicate_required_models_err)

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


def check_duplicate_required_models(
    visit: Visit,
    visit_crf_collection: CrfCollection,
    visit_type: str,
) -> Error | None:
    if duplicates := get_duplicates(
        list_items=[
            *get_required_models(collection=visit_crf_collection),
            *get_models(collection=visit.crfs_prn),
        ]
    ):
        return Error(
            "Required model class appears more than once for a visit. "
            f"Got '{visit}' '{visit_type}' visit Crf collection. "
            f"Duplicates {[d._meta.label_lower for d in duplicates]}",
            id="edc_visit_schedule.002",
        )


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
            f"Proxy root/child models: {proxy_root_child_pairs=}",
            id="edc_visit_schedule.003",
        )


def check_multiple_proxies_same_proxy_root(
    visit: Visit,
    visit_crf_collection: CrfCollection,
    visit_type: str,
) -> Error | None:
    all_proxy_models = get_proxy_models(collection=visit_crf_collection) + get_proxy_models(
        collection=visit.crfs_prn
    )
    proxy_roots = [get_proxy_root_model(m) for m in all_proxy_models]

    if duplicate_proxy_roots := get_duplicates(proxy_roots):
        # Determine if there is a clash with multiple proxies with the same proxy root model
        non_shared_proxy_root_models = get_proxy_models(
            collection=CrfCollection(
                *[f for f in visit_crf_collection if not f.shares_proxy_root]
            )
        ) + get_proxy_models(
            collection=CrfCollection(*[f for f in visit.crfs_prn if not f.shares_proxy_root])
        )

        proxy_root_clashes = defaultdict(list)
        for pm in non_shared_proxy_root_models:
            proxy_root_model = get_proxy_root_model(pm)
            if proxy_root_model in duplicate_proxy_roots:
                proxy_root_clashes[proxy_root_model._meta.label_lower].append(
                    pm._meta.label_lower
                )

        # Prepare error message and add
        if proxy_root_clashes:
            shared_proxy_root_models = get_proxy_models(
                collection=CrfCollection(
                    *[f for f in visit_crf_collection if f.shares_proxy_root]
                )
            ) + get_proxy_models(
                collection=CrfCollection(*[f for f in visit.crfs_prn if f.shares_proxy_root])
            )
            for pm in shared_proxy_root_models:
                proxy_root_model = get_proxy_root_model(pm)
                if proxy_root_model in duplicate_proxy_roots:
                    clash_desc = proxy_root_clashes[proxy_root_model._meta.label_lower]
                    clash_desc.append(pm._meta.label_lower)
                    clash_desc.sort()

            return Error(
                "Multiple proxies with same proxy root model appear for "
                "a visit. If this is intentional, consider using "
                "`shares_proxy_root` argument when defining Crf. "
                f"Got '{visit}' '{visit_type}' visit Crf collection. "
                f"Proxy root/child models: {proxy_root_clashes=}",
                id="edc_visit_schedule.004",
            )


def get_models(collection: CrfCollection) -> list[models.Model]:
    return [f.model_cls for f in collection]


def get_required_models(collection: CrfCollection) -> list[models.Model]:
    return [f.model_cls for f in collection if f.required]


def get_proxy_models(collection: CrfCollection) -> list[models.Model]:
    return [f.model_cls for f in collection if f.model_cls._meta.proxy]


def get_proxy_root_model(proxy_model: models.Model) -> models.Model | None:
    """Returns proxy's root (concrete) model if `proxy_model` is a
    proxy model, else returns None.
    """
    if proxy_model._meta.proxy:
        return proxy_model._meta.concrete_model
