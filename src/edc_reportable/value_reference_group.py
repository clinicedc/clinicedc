from __future__ import annotations

from typing import TYPE_CHECKING

from .utils import get_references_by_criteria

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
    """Groups normal or grading references as a dictionary."""

    def __init__(self, name: str = None):
        self.name = name
        self.normal: dict[str, list] = {}
        self.grading: dict[str, list] = {}

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

    def add_normal(self, normal_reference: NormalReference):
        """Adds a ValueReference to the dictionary of normal
        references.
        """
        self._add(normal_reference, self.normal)

    def add_grading(self, grade_reference: GradeReference):
        """Adds a GradeReference to the dictionary of grading
        references.
        """
        self._add(grade_reference, self.grading)

    def get_normal_description(self, **kwargs) -> list[str]:
        """Returns the descriptions of the normal references for
        these criteria as a list.
        """
        descriptions = []
        for value_ref in self._get_normal_references(**kwargs):
            descriptions.append(value_ref.description())
        return descriptions

    def get_normal(self, value: int | float = None, **kwargs):
        """Returns a Normal instance or None."""
        normal = None
        for value_ref in self._get_normal_references(**kwargs):
            if value_ref.in_bounds(value=value, **kwargs):
                if not normal:
                    normal = Normal(value, value_ref.description)
                else:
                    raise BoundariesOverlap(
                        f"Previously got {normal}. "
                        f"Got {value_ref.description(value=value)}. "
                        "Check your definitions."
                    )
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

    def _get_normal_references(self, **kwargs):
        """Returns a list of ValueReference instances or raises."""
        references = get_references_by_criteria(value_references=self.normal, **kwargs)
        if not references:
            raise NotEvaluated(
                f"{self.name} value not evaluated. "
                f"Normal reference range not found. Using criteria {kwargs}. "
                f"See {repr(self)}."
            )
        return references

    def _get_grading_references(self, **kwargs):
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

    def _add(
        self,
        value_reference: GradeReference | NormalReference,
        value_references: dict[str, list[NormalReference | GradeReference]],
    ) -> None:
        """Add value reference to the group by gender."""
        if value_reference.name != self.name:
            raise InvalidValueReference(
                "Cannot add to group; name does not match. "
                f"Expected '{self.name}'. Got '{value_reference.name}'. "
                f"See {repr(value_reference)}"
            )
        try:
            if value_reference in value_references[value_reference.gender]:
                raise ValueReferenceAlreadyAdded(
                    f"Value reference {value_reference} has already been added."
                )
        except KeyError:
            value_references[value_reference.gender] = []
        value_references[value_reference.gender].append(value_reference)
