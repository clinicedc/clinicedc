from .value_reference import ValueReference


class GradeReference(ValueReference):

    def __init__(self, grade=None, **kwargs):
        self.grade = int(grade)
        super().__init__(**kwargs)

    def __repr__(self):
        return (f'{super().__repr__()} GRADE {self.grade})')

    def description(self, **kwargs):
        return f'{self.evaluator.description(**kwargs)} GRADE {self.grade}'
