from __future__ import annotations

from typing import TYPE_CHECKING

from .normal_reference import NormalReferenceError
from .utils import get_normal_reference, get_references_by_criteria

if TYPE_CHECKING:
    from .grade_reference import GradeReference
    from .normal_reference import NormalReference

GRADING = "grading"
NORMAL = "normal"


class InvalidValueReference(Exception):
    pass


class ValueReferenceNotFound(Exception):
    pass


class ValueReferenceAlreadyAdded(Exception):
    pass


class BoundariesOverlap(Exception):
    pass


class NotEvaluated(Exception):
    pass


class Result:
    def __init__(self, value, description):
        self._value = value
        self.description = description(value=value)

    def __str__(self):
        return self.description


class Normal(Result):
    pass


class Grade(Result):
    def __init__(self, value, grade, description):
        super().__init__(value, description)
        self.grade = grade


class ValueReferenceGroup:
    """Groups normal or grading references as lists."""

    def __init__(self, name: str = None):
        self.name = name
        self.normal: list[NormalReference] = []
        self.grading: list[GradeReference] = []

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

    def add_normal(self, normal_reference: NormalReference):
        """Adds a ValueReference to the list of normal references."""
        if normal_reference.name != self.name:
            raise InvalidValueReference(
                "Cannot add normal reference to group; name does not match. "
                f"Expected '{self.name}'. Got '{normal_reference.name}'. "
                f"See {repr(normal_reference)}"
            )
        elif normal_reference in self.normal:
            raise ValueReferenceAlreadyAdded(
                f"Normal reference {normal_reference} has already been added."
            )
        else:
            self.normal.append(normal_reference)

    def add_grading(self, grade_reference: GradeReference):
        """Adds a GradeReference to the list of grading references."""
        if grade_reference.name != self.name:
            raise InvalidValueReference(
                "Cannot add grading reference to group; name does not match. "
                f"Expected '{self.name}'. Got '{grade_reference.name}'. "
                f"See {repr(grade_reference)}"
            )

        if grade_reference in self.grading:
            raise ValueReferenceAlreadyAdded(
                f"Grading reference {grade_reference} has already been added."
            )
        else:
            self.grading.append(grade_reference)

    def get_normal_description(self, **kwargs) -> list[str]:
        """Returns the descriptions of the normal references for
        these criteria as a list.
        """
        descriptions = []
        for value_ref in self._get_normal_references(**kwargs):
            descriptions.append(value_ref.description())
        return descriptions

    def get_normal(self, value: int | float = None, gender=None, units=None, **kwargs):
        """Returns a Normal instance or None."""
        normal = None
        normal_reference = get_normal_reference(
            name=self.name,
            gender=gender,
            units=units,
            normal_references=self.normal,
            exception_cls=NormalReferenceError,
        )
        if normal_reference.in_bounds(value=value, units=units):
            normal = Normal(value, normal_reference.description)
        return normal

    def get_grade(self, value=None, **kwargs):
        """Returns a Grade instance or None."""
        grade = None
        for grade_ref in self._get_grading_references(**kwargs):
            if grade_ref.in_bounds(value=value, **kwargs):
                if not grade:
                    grade = Grade(value, grade_ref.grade, grade_ref.description)
                else:
                    raise BoundariesOverlap(
                        f"Previously got {grade}. "
                        f"Got {grade_ref.description(value=value)} ",
                        "Check your definitions.",
                    )
        return grade

    def _get_normal_references(self, **kwargs) -> list[NormalReference]:
        """Returns a list of ValueReference instances or raises."""
        references = get_references_by_criteria(value_references=self.normal, **kwargs)
        if not references:
            raise NotEvaluated(
                f"{self.name} value not evaluated. "
                f"Normal reference range not found. Using criteria {kwargs}. "
                f"See {repr(self)}."
            )
        return references

    def _get_grading_references(self, **kwargs) -> list[GradeReference]:
        """Returns a list of GradeReference instances or raises."""
        references = get_references_by_criteria(value_references=self.grading, **kwargs)
        if not references:
            raise NotEvaluated(
                f"{self.name} value not graded. "
                f"Grading reference range not found. Using criteria {kwargs}. "
                f"See {repr(self)}."
            )
        references.sort(key=lambda x: x.grade, reverse=True)
        return references
