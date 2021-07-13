from django.conf import settings
from edc_constants.constants import NO, YES
from edc_model.utils import duration_to_date

try:
    DIAGNOSIS_LABELS = getattr(settings, "EDC_DIAGNOSIS_LABELS")
except AttributeError as e:
    raise AttributeError(
        f"{e}. Expected something like `EDC_DIAGNOSIS_LABELS=dict"
        "(hiv=HIV,dm=Diabetes,htn=Hypertension,chol=High Cholesterol)`"
    )


def calculate_dx_date_if_estimated(
    dx_date,
    dx_ago,
    report_datetime,
):
    if dx_ago and not dx_date:
        dx_estimated_date = duration_to_date(dx_ago, report_datetime)
        dx_date_estimated = YES
    else:
        dx_estimated_date = None
        dx_date_estimated = NO
    return dx_estimated_date, dx_date_estimated


def get_condition_abbreviations():
    return [k for k in DIAGNOSIS_LABELS]


def get_diagnosis_labels():
    return DIAGNOSIS_LABELS
