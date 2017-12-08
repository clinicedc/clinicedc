from .age_evaluator import AgeEvaluator
from .evaluator import Evaluator, ValueBoundryError


class ValueReference:

    age_evaluator_cls = AgeEvaluator
    evaluator_cls = Evaluator

    def __init__(self, name=None, gender=None, **kwargs):
        self.name = name
        if isinstance(gender, (list, tuple)):
            self.gender = ''.join(gender)
        else:
            self.gender = gender
        self.evaluator = self.evaluator_cls(name=name, **kwargs)
        self.age_evaluator = self.age_evaluator_cls(**kwargs)
        self.success = {}
        self.error = {}

    def __repr__(self):
        return (f'{self.__class__.__name__}({self.name}, {self.description()}, '
                f'{self.gender}, {self.age_evaluator.description("AGE")})')

    def in_bounds(self, value=None, **kwargs):
        try:
            in_bounds = self.evaluator.in_bounds_or_raise(value, **kwargs)
        except ValueBoundryError:
            in_bounds = False
            self.error = {self.name: self.description(value=value)}
        else:
            self.success = {self.name: self.description(value=value)}
        return in_bounds

    def description(self, **kwargs):
        return self.evaluator.description(**kwargs)

    def age_match(self, dob=None, report_datetime=None, age_units=None):
        try:
            age_match = self.age_evaluator.in_bounds_or_raise(
                dob=dob, report_datetime=report_datetime, age_units=age_units)
        except ValueBoundryError:
            age_match = False
        return age_match
