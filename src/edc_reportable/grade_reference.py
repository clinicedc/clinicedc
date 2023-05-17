from .constants import GRADE0, GRADE1, GRADE2, GRADE3, GRADE4, GRADE5
from .value_reference import ValueReference


class GradeError(Exception):
    pass


class GradeReference(ValueReference):
    grades: list[str] = [GRADE0, GRADE1, GRADE2, GRADE3, GRADE4, GRADE5]

    def __init__(self, grade: int = None, normal_references: dict = None, func=None, **kwargs):
        if int(grade) not in [int(x) for x in self.grades]:
            raise GradeError(f"Invalid grade. Expected one of {self.grades}. Got {grade}.")
        self.grade: int = int(grade)
        super().__init__(normal_references=normal_references, func=func, **kwargs)

    def __repr__(self):
        return f"{super().__repr__()} GRADE {self.grade})"

    def description(self, **kwargs):
        return f"{self.evaluator.description(**kwargs)} GRADE {self.grade}"
