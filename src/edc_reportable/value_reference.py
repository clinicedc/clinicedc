from typing import Optional, Union

from .age_evaluator import AgeEvaluator
from .evaluator import Evaluator, ValueBoundryError
from .parsers import parse_boundary


class ValueReferenceError(Exception):
    pass


class ValueReference:
    age_evaluator_cls = AgeEvaluator
    evaluator_cls = Evaluator

    def __init__(
        self,
        name: Optional[str] = None,
        gender: Optional[str] = None,
        units: Optional[str] = None,
        normal_references=None,
        **kwargs,
    ):
        self._normal_reference = None
        self.normal_references = normal_references
        self.name = name
        self.units = units
        if isinstance(gender, (list, tuple)):
            self.gender = "".join(gender)
        else:
            self.gender = gender
        kwargs["lower"] = self.get_boundary_value(kwargs["lower"])
        kwargs["upper"] = self.get_boundary_value(kwargs["upper"])
        self.evaluator = self.evaluator_cls(name=self.name, units=units, **kwargs)
        self.age_evaluator = self.age_evaluator_cls(**kwargs)
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

    @property
    def normal_reference(self):
        if not self._normal_reference:
            if self.normal_references:
                self._normal_reference = [
                    x[0] for x in self.normal_references.values() if x[0].units == self.units
                ]
            else:
                raise ValueReferenceError(
                    f"Normal references not provided. Got {self.name} per {self.units}"
                )
            if not self._normal_reference:
                opts = [(x[0].name, x[0].units) for x in self.normal_references.values()]
                raise ValueReferenceError(
                    "Normal reference not found. Expected one "
                    f"of {opts}. Got {self.name} per {self.units}"
                )
        return self._normal_reference[0]

    def get_boundary_value(self, value: str) -> Union[int, float]:
        """Return value as a literal value or as a value relative
        to the normal lower or upper normal.
        """
        try:
            value = value.upper()
        except AttributeError:
            pass
        else:
            lln, uln = parse_boundary(value)
            value = (
                lln * self.normal_reference.lower if lln else uln * self.normal_reference.upper
            )
        return value
