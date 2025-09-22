from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.conf import settings

from ..formula import Formula
from .get_default_reportable_grades import get_default_reportable_grades
from .reference_range_colllection_model_cls import reference_range_colllection_model_cls
from .update_grading_data import update_grading_data
from .update_grading_exceptions import update_grading_exceptions
from .update_normal_data import update_normal_data

if TYPE_CHECKING:
    from ..models import ReferenceRangeCollection


class AlreadyLoaded(Exception):
    pass


__all__ = ["load_all_reference_ranges", "load_reference_ranges"]


def get_module_name() -> str:
    return getattr(settings, "EDC_REPORTABLE_DEFAULT_MODULE_NAME", "reportables")


def load_all_reference_ranges() -> None:
    """Check each app and load the reference ranges if the module
    exists.

    Typically called by post_migrate.
    """
    module_name = get_module_name()
    sys.stdout.write(f" * checking for site {module_name} ...\n")
    for app in django_apps.app_configs:
        try:
            reportables_module = import_module(f"{app}.{module_name}")
        except ImportError:
            pass
        else:
            load_reference_ranges(
                reportables_module.collection_name,
                normal_data=reportables_module.normal_data,
                grading_data=reportables_module.grading_data,
                reportable_grades=reportables_module.reportable_grades,
                reportable_grades_exceptions=reportables_module.reportable_grades_exceptions,
            )
            sys.stdout.write(
                f"   - loaded {app}.{module_name} collection "
                f"`{reportables_module.collection_name}`."
            )


def load_reference_ranges(
    collection_name: str,
    normal_data: dict[str, list[Formula]],
    grading_data: dict[str, list[Formula]],
    reportable_grades: list[int] | None = None,
    reportable_grades_exceptions: dict[str, list[int]] | None = None,
    keep_existing: bool | None = None,
    create_missing_normal: bool | None = None,
) -> ReferenceRangeCollection:
    """Load the reference ranges for a single collection.

    See also: load_all_reference_ranges
    """
    (
        reference_range_collection,
        _,
    ) = reference_range_colllection_model_cls().objects.get_or_create(name=collection_name)
    reportable_grades = reportable_grades or get_default_reportable_grades()
    for grade in reportable_grades:
        setattr(reference_range_collection, f"grade{grade}", True)
    reference_range_collection.save()

    update_grading_exceptions(
        reference_range_collection=reference_range_collection,
        reportable_grades_exceptions=reportable_grades_exceptions,
        keep_existing=keep_existing,
    )

    update_normal_data(reference_range_collection, normal_data=normal_data)

    update_grading_data(
        reference_range_collection,
        grading_data=grading_data,
        reportable_grades=reportable_grades,
        reportable_grades_exceptions=reportable_grades_exceptions,
        create_missing_normal=True,
    )
    return reference_range_collection
