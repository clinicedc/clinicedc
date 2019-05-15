from .age_evaluator import AgeEvaluator
from .evaluator import Evaluator, ValueBoundryError


class ValueReference:

    age_evaluator_cls = AgeEvaluator
    evaluator_cls = Evaluator

    def __init__(self, name=None, gender=None, units=None, **kwargs):
        self.name = name
        self.units = units
        if isinstance(gender, (list, tuple)):
            self.gender = "".join(gender)
        else:
            self.gender = gender
        self.age_evaluator = self.age_evaluator_cls(**kwargs)
        self.evaluator = self.evaluator_cls(name=self.name, units=units, **kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.description()})"

    def description(self, **kwargs):
        return (
            f"{self.evaluator.description(**kwargs)} {self.gender} "
            f"{self.age_evaluator.description()}"
        )

    def in_bounds(self, value=None, **kwargs):
        try:
            in_bounds = self.evaluator.in_bounds_or_raise(value, **kwargs)
        except ValueBoundryError:
            in_bounds = False
        return in_bounds

    def age_match(self, dob=None, report_datetime=None, age_units=None):
        try:
            age_match = self.age_evaluator.in_bounds_or_raise(
                dob=dob, report_datetime=report_datetime, age_units=age_units
            )
        except ValueBoundryError:
            age_match = False
        return age_match
