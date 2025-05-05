from __future__ import annotations

import copy
import csv
import os
import sys
from datetime import datetime
from importlib import import_module
from inspect import isfunction

from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.color import color_style
from django.db import transaction
from django.utils.module_loading import module_has_submodule
from edc_list_data.site_list_data import AlreadyLoaded

from .constants import GRADE3, GRADE4
from .exceptions import SiteReportablesError
from .formula import Formula
from .grade_reference import GradeReference
from .normal_reference import NormalReference
from .reference_range_collection import ReferenceRangeCollection
from .utils import get_references_by_criteria
from .value_reference_group import GRADING, NORMAL, ValueReferenceGroup


class MissingNormalReference(Exception):
    pass


def get_autodiscover_enabled():
    return getattr(settings, "EDC_REPORTABL_ENABLE_AUTODISCOVER", True)


class SiteReportables:

    default_module_prefixes = ["edc_"]
    default_module_name = "reportables"
    default_reportable_grades = [GRADE3, GRADE4]

    def __init__(self, module_name=None):
        self.registry = {}
        self.collection_names = []
        self.module_name = module_name or self.default_module_name

    def load(self, module: str = None):
        """Load data on post_migrate"""
        from .models import update_grading_data, update_normal_data

        collection_name = getattr(module, "name", None)
        if collection_name in self.collection_names:
            raise AlreadyLoaded(
                f"Reportable collection already loaded. Got `{collection_name}`."
            )
        else:
            self.collection_names.append(collection_name)
            update_normal_data(
                collection_name, normal_data=getattr(module, "normal_data", None)
            )
            update_grading_data(
                collection_name,
                grading_data=getattr(module, "grading_date", None),
                reportable_grades=getattr(module, "reportable_grades", None),
                reportable_grades_exceptions=getattr(
                    module, "reportable_grades_exceptions", None
                ),
            )
            sys.stdout.write(
                f"   - loaded {self.module_name} collection `{collection_name}` "
                f"from '{module.__name__}'\n"
            )

    def register(
        self,
        name: str | None = None,
        normal_data: dict[str, list[Formula]] | None = None,
        grading_data: dict[str, list] | None = None,
        reportable_grades: dict | None = None,
        reportable_grades_exceptions: dict | None = None,
    ):
        pass

    def register2(
        self,
        name: str | None = None,
        normal_data: dict[str, list[Formula]] | None = None,
        grading_data: dict[str, list] | None = None,
        reportable_grades: dict | None = None,
        reportable_grades_exceptions: dict | None = None,
    ):
        """Read in dictionaries of normal and grading formulas from a
        reportables.py.

        Register all to a ReferenceRangeCollection instance and finally
        add the ReferenceRangeCollection to this controller's
        registry dictionary.

        For example:

            site_reportables.register(
                name="effect",
                normal_data=normal_data,
                grading_data=grading_data)

        """
        # get or create the reference_range_collection for this
        # reportables file
        if name in self._registry:
            reference_range_collection = self._registry.get(name)
        else:
            reference_range_collection = ReferenceRangeCollection(
                name=name,
                reportable_grades=reportable_grades,
                reportable_grades_exceptions=reportable_grades_exceptions,
            )

        # register_normal_formulas
        for name, normal_formulas in normal_data.items():
            value_ref_grp = ValueReferenceGroup(name=name)
            for formula in normal_formulas:
                for gender_str in formula.gender:
                    for gender in gender_str:
                        new_formula = copy.copy(formula)
                        new_formula.gender = gender
                        normal_reference = NormalReference(name=name, **new_formula.__dict__)
                        value_ref_grp.add_normal(normal_reference)
            reference_range_collection.register(value_ref_grp)
        # register_grading_formulas
        for name, grading_formulas in grading_data.items():
            value_ref_grp = reference_range_collection.get(name)
            if not value_ref_grp:
                raise MissingNormalReference(
                    f"Attempting to add grading for item without a "
                    f"normal reference. Got {name}."
                )
            for formula in grading_formulas:
                if isfunction(formula):
                    grade_ref = GradeReference(
                        name=name,
                        func=formula,
                        normal_references=value_ref_grp.normal,
                    )
                else:
                    grade_ref = GradeReference(
                        name=name,
                        normal_references=value_ref_grp.normal,
                        **formula.__dict__,
                    )
                value_ref_grp.add_grading(grade_ref)
            reference_range_collection.update_grp(value_ref_grp)

        # add reference_range_collection to site_reportables key=name
        site_reportables._registry.update(
            {reference_range_collection.name: reference_range_collection}
        )

    def _import_on_migrate(self, module) -> None:
        opts: dict = {}
        opts.update(normal_data=getattr(module, "normal_data", None))
        opts.update(grading_date=getattr(module, "grading_date", None))
        opts.update(list_data_model_name=getattr(module, "list_data_model_name", None))
        opts.update(apps=getattr(module, "apps", None))

        for module_name, opts in self.registry.items():
            sys.stdout.write(f"   - loading {module_name} ... \r")
            try:
                with transaction.atomic():
                    pass
                    # load here
                    # obj = PreloadData(**opts)
                    # sys.stdout.write(
                    #     f"   - loading {module_name} ... {obj.item_count} items.\n"
                    # )
            except SiteReportablesError as e:
                style = color_style()
                sys.stdout.write(style.ERROR(f"ERROR! {e}\n"))

    @staticmethod
    def _read_module(module) -> dict:
        opts: dict = {}
        opts.update(normal_data=getattr(module, "normal_data", None))
        opts.update(grading_data=getattr(module, "grading_data", None))
        opts.update(list_data_model_name=getattr(module, "list_data_model_name", None))
        opts.update(apps=getattr(module, "apps", None))
        # if not any([x for x in opts.values()]):
        #     raise SiteListDataError(f"Invalid list_data module. See {module}")
        return opts

    def get(self, name: str):
        """Given a UTESTID, return the ReferenceRangeCollection instance"""
        return self._registry.get(name)

    def get_normal(
        self,
        name,
        gender: list[str] | None = None,
        units: str | None = None,
        dob: datetime | None = None,
    ):
        normal_references = self._registry.get(name)[NORMAL]
        normal_references = get_references_by_criteria(normal_references, gender, dob)
        if not normal_references:
            raise SiteReportablesError(f"Normal references not found. Got {name} [{gender}]")
        elif len(normal_references) > 1:
            raise SiteReportablesError(
                f"Multiple references found. Got {name} {units} [{gender}]"
            )

        # return self._registry.get(name)[NORMAL]
        return normal_references[0]

    def get_grading(self, name):
        return self._registry.get(name)[GRADING]

    def get_reportable_grades(self, name):
        return self._registry.get(name).reportable_grades

    def read_csv(self, name=None, path=None):
        pass

    def to_csv(self, collection_name=None, path=None):
        path = path or "~/"
        path = os.path.expanduser(path)
        filename1 = os.path.join(path, f"{collection_name}_normal_ranges.csv")
        filename2 = os.path.join(path, f"{collection_name}_grading.csv")
        reference_range_collection = self.get(collection_name)
        data = reference_range_collection.as_data()
        try:
            fieldnames = list(data.get(NORMAL)[0].keys())
        except IndexError:
            pass
        else:
            fieldnames.insert(1, "description")
            with open(filename1, "w") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for formula in data.get(NORMAL):
                    writer.writerow(formula)
        try:
            fieldnames = list(data.get(GRADING)[0].keys())
        except IndexError:
            pass
        else:
            fieldnames.insert(1, "description")
            with open(filename2, "w") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for formula in data.get(GRADING):
                    writer.writerow(formula)
        return filename1, filename2

    def autodiscover(self) -> None:
        if get_autodiscover_enabled():
            if "migrate" in sys.argv:
                sys.stdout.write(f" * checking for data from  `{self.module_name}` ...\n")
                for app_name in django_apps.app_configs:
                    try:
                        self._import_on_migrate(app_name)
                    except ModuleNotFoundError:
                        pass
            elif "makemigrations" not in sys.argv and "showmigrations" not in sys.argv:
                sys.stdout.write(f" * checking apps for `{self.module_name}` ...\n")
                pass

    def autodiscover_old(self, module_name=None, verbose=True):
        module_name = module_name or "reportables"
        writer = sys.stdout.write if verbose else lambda x: x
        style = color_style()
        writer(f" * checking for site {module_name} ...\n")
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_reportables._registry)
                    import_module(f"{app}.{module_name}")
                    writer(f"   - registered '{module_name}' from '{app}'\n")
                except SiteReportablesError as e:
                    writer(f"   - loading {app}.{module_name} ... ")
                    writer(style.ERROR(f"ERROR! {e}\n"))
                except ImportError as e:
                    site_reportables._registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SiteReportablesError(str(e))
            except ImportError:
                pass
            except Exception as e:
                raise SiteReportablesError(
                    f"{e.__class__.__name__} was raised when loading {module_name}. "
                    f"Got {e} See {app}.{module_name}"
                )


site_reportables = SiteReportables()
