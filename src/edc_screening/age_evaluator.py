from edc_reportable import AgeEvaluator as ReportableAgeEvaluator, ValueBoundryError
from django.utils.timezone import localtime
from edc_utils.date import get_utcnow
from dateutil.relativedelta import relativedelta


class AgeEvaluator(ReportableAgeEvaluator):
    def __init__(self, **kwargs):
        self.reasons_ineligible = None
        super().__init__(**kwargs)

    def eligible(self, age=None):
        age = age or 18
        self.reasons_ineligible = None
        eligible = False
        if age:
            try:
                self.in_bounds_or_raise(age=age)
            except ValueBoundryError as e:
                self.reasons_ineligible = str(e)  # "age<18."
            else:
                eligible = True
        return eligible

    def in_bounds_or_raise(self, age=None):
        self.reasons_ineligible = None
        dob = localtime(get_utcnow() - relativedelta(years=age)).date()
        age_units = "years"
        report_datetime = localtime(get_utcnow())
        return super().in_bounds_or_raise(
            dob=dob, report_datetime=report_datetime, age_units=age_units
        )
