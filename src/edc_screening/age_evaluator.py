from typing import Optional

from dateutil.relativedelta import relativedelta
from django.utils.timezone import localtime
from edc_reportable import AgeEvaluator as ReportableAgeEvaluator
from edc_reportable import ValueBoundryError
from edc_utils.date import get_utcnow


class AgeEvaluator(ReportableAgeEvaluator):
    def __init__(self, **kwargs) -> None:
        self.reasons_ineligible: Optional[str] = None
        super().__init__(**kwargs)

    def eligible(self, age: Optional[int] = None) -> bool:
        self.reasons_ineligible = None
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
        self.reasons_ineligible = None
        dob = localtime(get_utcnow() - relativedelta(years=age)).date()
        age_units = "years"
        report_datetime = localtime(get_utcnow())
        return super().in_bounds_or_raise(
            dob=dob, report_datetime=report_datetime, age_units=age_units
        )
