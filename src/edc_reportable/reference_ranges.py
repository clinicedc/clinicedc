from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..formula import Formula


class ReferenceRanges:
    def __init__(
        self,
        collection_name: str,
        *,
        normal_data: dict[str, list[Formula]] = None,
        grading_data: dict[str, list] = None,
        reportable_grades: dict | None = None,
        reportable_grades_exceptions: dict | None = None,
    ):
        self.collection_name = collection_name
        self.normal_data = normal_data
        self.grading_data = grading_data
        self.reportable_grades = reportable_grades
        self.reportable_grades_exceptions = reportable_grades_exceptions

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.collection_name}')"

    def __str__(self):
        return self.collection_name
