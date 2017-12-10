from .value_reference import ValueReference

GRADE1 = '1'
GRADE2 = '2'
GRADE3 = '3'
GRADE4 = '4'
GRADE5 = '5'


class GradeError(Exception):
    pass


class GradeReference(ValueReference):

    grades = [GRADE1, GRADE2, GRADE3, GRADE4, GRADE5]

    def __init__(self, grade=None, **kwargs):
        if grade not in self.grades:
            raise GradeError(
                f'Invalid grade. Expected one of {self.grades}. Got {grade}.')
        self.grade = int(grade)
        super().__init__(**kwargs)

    def __repr__(self):
        return (f'{super().__repr__()} GRADE {self.grade})')

    def description(self, **kwargs):
        return f'{self.evaluator.description(**kwargs)} GRADE {self.grade}'
