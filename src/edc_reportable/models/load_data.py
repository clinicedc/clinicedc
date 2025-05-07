import sys
from importlib import import_module

from django.apps import apps as django_apps
from django.conf import settings

from ..formula import Formula
from .reference_range_collection import ReferenceRangeCollection
from .utils import update_grading_data, update_normal_data


class AlreadyLoaded(Exception):
    pass


def get_module_name() -> str:
    return getattr(settings, "EDC_REPORTABLE_DEFAULT_MODULE_NAME", "reportables")


def load_all_reference_ranges():
    """Check each app and load the reference ranges if the module
    exists.

    Typically called by post_migrate.
    """
    collection_names: list[str] = []
    module_name = get_module_name()
    sys.stdout.write(f" * checking for site {module_name} ...\n")
    for app in django_apps.app_configs:
        try:
            reportables_module = import_module(f"{app}.{module_name}")
        except ImportError:
            pass
        else:
            reference_ranges = getattr(reportables_module, "reference_ranges", None)
            if reference_ranges:
                if reference_ranges.collection_name in collection_names:
                    raise AlreadyLoaded(
                        f"Reportable collection already loaded. Got `{reference_ranges}`."
                    )
                load_reference_ranges(
                    reference_ranges.collection_name,
                    normal_data=reference_ranges.normal_data,
                    grading_data=reference_ranges.grading_data,
                    reportable_grades=reference_ranges.reportable_grades,
                    reportable_grades_exceptions=reference_ranges.reportable_grades_exceptions,
                )
                collection_names.append(reference_ranges.collection_name)
                sys.stdout.write(
                    f"   - loaded {app}.{module_name} collection "
                    f"`{reference_ranges.collection_name}` "
                )


def load_reference_ranges(
    collection_name: str,
    normal_data: dict[str, list[Formula]] = None,
    grading_data: dict[str, list[Formula]] = None,
    reportable_grades: list[int] = None,
    reportable_grades_exceptions: dict[str, list[int]] = None,
):
    """Load the reference ranges for a single collection.

    See also: load_all_reference_ranges
    """
    reference_collection_name, _ = ReferenceRangeCollection.objects.get_or_create(
        name=collection_name
    )
    update_normal_data(reference_collection_name, normal_data=normal_data)
    update_grading_data(
        reference_collection_name,
        grading_data=grading_data,
        reportable_grades=reportable_grades,
        reportable_grades_exceptions=reportable_grades_exceptions,
    )
