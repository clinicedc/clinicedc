import sys
from importlib import import_module

from django.apps import apps as django_apps
from django.conf import settings

from .reference_range_collection import ReferenceRangeCollection
from .update_grading_data import update_grading_data
from .update_normal_data import update_normal_data


class AlreadyLoaded(Exception):
    pass


def get_module_name() -> str:
    return getattr(settings, "EDC_REPORTABLE_DEFAULT_MODULE_NAME", "reportables")


def load_data():
    """Load data on post_migrate"""
    collection_names: list[str] = []
    module_name = get_module_name()
    sys.stdout.write(f" * checking for site {module_name} ...\n")
    if True:  # "migrate" in sys.argv:
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
                    else:
                        collection_names.append(reference_ranges.collection_name)
                        reference_collection_name, _ = (
                            ReferenceRangeCollection.objects.get_or_create(
                                name=reference_ranges.collection_name
                            )
                        )
                        update_normal_data(
                            reference_collection_name, normal_data=reference_ranges.normal_data
                        )
                        update_grading_data(
                            reference_collection_name,
                            grading_data=reference_ranges.grading_data,
                            reportable_grades=reference_ranges.reportable_grades,
                            reportable_grades_exceptions=(
                                reference_ranges.reportable_grades_exceptions
                            ),
                        )
                        sys.stdout.write(
                            f"   - loaded {app}.{module_name} collection "
                            f"`{reference_ranges.collection_name}` "
                        )
