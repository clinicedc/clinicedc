import copy
import csv
import os
import sys

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import module_has_submodule
from importlib import import_module

from .grade_reference import GradeReference
from .normal_reference import NormalReference
from .parsers import unparse
from .reference_collection import ReferenceCollection
from .value_reference_group import ValueReferenceGroup, GRADING, NORMAL


class SiteReportablesError(Exception):
    pass


class MissingNormalReference(Exception):
    pass


class Reportables:
    def __init__(self):
        self._registry = {}

    def __iter__(self):
        return iter(self._registry.items())

    def register(self, name=None, normal_data=None, grading_data=None):
        if name in self._registry:
            reference_collection = self._registry.get(name)
        else:
            reference_collection = ReferenceCollection(name=name)
        for name, datas in normal_data.items():
            grp = ValueReferenceGroup(name=name)
            for data in datas:
                val_ref = NormalReference(name=name, **data)
                grp.add_normal(val_ref)
            reference_collection.register(grp)
        for name, datas in grading_data.items():
            grp = reference_collection.get(name)
            if not grp:
                raise MissingNormalReference(
                    f"Attempting to add grading for item without a "
                    f"normal reference. Got {name}."
                )
            for data in datas:
                grade_ref = GradeReference(name=name, **data)
                grp.add_grading(grade_ref)
            reference_collection.update_grp(grp)
        site_reportables._registry.update(
            {reference_collection.name: reference_collection}
        )

    def get(self, name):
        return self._registry.get(name)

    def get_normal(self, name):
        return self._registry.get(name)[NORMAL]

    def get_grading(self, name):
        return self._registry.get(name)[GRADING]

    def read_csv(self, name=None, path=None):
        pass

    def to_csv(self, collection_name=None, path=None):
        path = path or "~/"
        path = os.path.expanduser(path)
        filename1 = os.path.join(path, f"{collection_name}_normal_ranges.csv")
        filename2 = os.path.join(path, f"{collection_name}_grading.csv")
        reference_collection = self.get(collection_name)
        data = reference_collection.as_data()
        try:
            fieldnames = list(data.get(NORMAL)[0].keys())
        except IndexError:
            pass
        else:
            fieldnames.insert(1, "description")
            with open(filename1, "w") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for dct in data.get(NORMAL):
                    dct.update(description=unparse(**dct))
                    writer.writerow(dct)
        try:
            fieldnames = list(data.get(GRADING)[0].keys())
        except IndexError:
            pass
        else:
            fieldnames.insert(1, "description")
            with open(filename2, "w") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for dct in data.get(GRADING):
                    dct.update(description=unparse(**dct))
                    writer.writerow(dct)
        return filename1, filename2

    def autodiscover(self, module_name=None, verbose=True):
        module_name = module_name or "reportables"
        writer = sys.stdout.write if verbose else lambda x: x
        style = color_style()
        writer(f" * checking for site {module_name} ...\n")
        for app in django_apps.app_configs:
            writer(f" * searching {app}           \r")
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_reportables._registry)
                    import_module(f"{app}.{module_name}")
                    writer(f" * registered '{module_name}' from '{app}'\n")
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


site_reportables = Reportables()
