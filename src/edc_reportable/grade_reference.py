from typing import Callable

from .constants import GRADE0, GRADE1, GRADE2, GRADE3, GRADE4, GRADE5
from .exceptions import GradeReferenceError
from .value_reference import ValueReference


class GradeReference(ValueReference):
    grades: list[str] = [GRADE0, GRADE1, GRADE2, GRADE3, GRADE4, GRADE5]

    def __init__(
        self,
        grade: int = None,
        normal_references: dict = None,
        func: Callable | None = None,
        **kwargs,
    ):
        if str(grade) not in self.grades:
            raise GradeReferenceError(
                f"Invalid grade. Expected one of {self.grades}. Got {grade}."
            )
        self.grade = grade
        super().__init__(normal_references=normal_references, func=func, **kwargs)

    def description(self, **kwargs):
        return f"{super().description(**kwargs)} GRADE {self.grade}"
