from typing import Optional

from .constants import GRADE3, GRADE4


class AlreadyRegistered(Exception):
    pass


class ReferenceRangeCollectionError(Exception):
    pass


class ReferenceRangeCollection:

    """Holds all normal and grading data available by name.

    Usually there is just one reference collection per project so
    name can be the project name.
    """

    def __init__(
        self,
        name=None,
        reportable_grades: Optional[list] = None,
        reportable_grades_exceptions: Optional[dict] = None,
    ):
        self.registry = {}
        self.name = name
        self.reportable_grades = reportable_grades or [GRADE3, GRADE4]
        self.reportable_grades_exceptions = reportable_grades_exceptions or {}
        for k in self.reportable_grades_exceptions:
            if k not in self.reportable_grades:
                raise ReferenceRangeCollectionError(
                    "Invalid reportable grades exception. UTEST_ID not found "
                    f"in grading table. Got {k}"
                )

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"

    def register(self, grp=None):
        if grp.name in self.registry:
            raise AlreadyRegistered(f"Got {repr(grp)}")
        else:
            self.registry.update({grp.name: grp})

    def get(self, name):
        return self.registry.get(name)

    def update_grp(self, grp):
        self.registry.update({grp.name: grp})

    def as_data(self):
        """Returns a dictionary of the normal and grading references
        in this collection.
        """
        exclude_attrs = [
            "evaluator",
            "age_evaluator",
            "_normal_reference",
            "normal_references",
        ]
        data = {"normal": [], "grading": []}
        for name, grp in self.registry.items():
            for normal_refs in grp.normal.values():
                for ref in normal_refs:
                    dct = ref.__dict__
                    dct.update(name=name)
                    dct = {k: v for k, v in dct.items() if k not in exclude_attrs}
                    data["normal"].append(dct)
        for name, grp in self.registry.items():
            for grade_refs in grp.grading.values():
                for ref in grade_refs:
                    dct = ref.__dict__
                    dct.update(name=name)
                    dct = {k: v for k, v in dct.items() if k not in exclude_attrs}
                    data["grading"].append(dct)
        return data
