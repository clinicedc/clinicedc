from edc_utils import age, get_utcnow

from .evaluator import Evaluator


class AgeEvaluator(Evaluator):
    def __init__(
        self,
        age_lower=None,
        age_upper=None,
        age_units=None,
        age_lower_inclusive=None,
        age_upper_inclusive=None,
        **kwargs,
    ):
        kwargs["units"] = age_units or "years"
        kwargs["lower"] = age_lower or 0
        kwargs["upper"] = age_upper
        kwargs["lower_inclusive"] = age_lower_inclusive
        kwargs["upper_inclusive"] = age_upper_inclusive
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.description(show_as_int=True)})"

    def description(self, value=None, **kwargs):
        kwargs["show_as_int"] = True
        kwargs["placeholder"] = "AGE"
        return super().description(value=value, **kwargs)

    def in_bounds_or_raise(self, dob=None, report_datetime=None, age_units=None):
        report_datetime = report_datetime or get_utcnow()
        age_units = age_units or "years"
        rdelta = age(dob, report_datetime)
        value = getattr(rdelta, self.units)
        return super().in_bounds_or_raise(value, units=age_units)
