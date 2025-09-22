from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.timezone import localtime

from edc_reportable.age_evaluator import AgeEvaluator as ReportableAgeEvaluator
from edc_reportable.exceptions import ValueBoundryError


class AgeEvaluator(ReportableAgeEvaluator):
    def __init__(self, **kwargs) -> None:
        self.reasons_ineligible: str = ""
        super().__init__(**kwargs)

    def eligible(self, age: int | None = None) -> bool:
        self.reasons_ineligible = ""
        eligible = False
        if age:
            try:
                self.in_bounds_or_raise(age=age)
            except ValueBoundryError as e:
                self.reasons_ineligible = str(e)
            else:
                eligible = True
        else:
            self.reasons_ineligible = "Age unknown"
        return eligible

    def in_bounds_or_raise(self, age: int = None, **kwargs):
        self.reasons_ineligible = ""
        dob = localtime(timezone.now() - relativedelta(years=age)).date()
        age_units = "years"
        report_datetime = localtime(timezone.now())
        return super().in_bounds_or_raise(
            dob=dob, report_datetime=report_datetime, age_units=age_units
        )
