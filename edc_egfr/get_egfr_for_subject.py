from datetime import date, datetime

from .egfr import Egfr


def get_egfr_for_subject(
    creatinine_value: float = None,
    creatinine_units: str = None,
    assay_datetime: datetime = None,
    dob: date = None,
    gender: str = None,
    ethnicity: str = None,
    report_datetime: datetime = None,
    baseline_egfr_value: float | None = None,
    value_threshold: float | None = None,
    percent_drop_threshold: float | None = None,
):
    return Egfr(
        percent_drop_threshold=percent_drop_threshold or 20.0000,
        dob=dob,
        gender=gender,
        ethnicity=ethnicity,
        value_threshold=value_threshold or 45.0000,
        report_datetime=report_datetime,
        baseline_egfr_value=baseline_egfr_value,
        formula_name="ckd-epi",
        reference_range_collection_name="meta",
        creatinine_units=creatinine_units,
        creatinine_value=creatinine_value,
        assay_datetime=assay_datetime,
    )
