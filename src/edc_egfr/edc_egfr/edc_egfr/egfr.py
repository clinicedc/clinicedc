from datetime import date, datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from edc_constants.constants import NEW
from edc_reportable import site_reportables
from edc_reportable.units import EGFR_UNITS, PERCENT
from edc_utils import age

from .calculators import EgfrCkdEpi, EgfrCockcroftGault, egfr_percent_change
from .get_drop_notification_model import get_egfr_drop_notification_model_cls


class EgfrError(Exception):
    pass


class Egfr:

    calculators = {"ckd-epi": EgfrCkdEpi, "cockcroft-gault": EgfrCockcroftGault}

    def __init__(
        self,
        report_datetime: Optional[datetime] = None,
        baseline_egfr_value: Optional[float] = None,
        gender: Optional[str] = None,
        ethnicity: Optional[str] = None,
        age_in_years: Optional[int] = None,
        dob: Optional[date] = None,
        creatinine_value: Optional[float] = None,
        creatinine_units: Optional[str] = None,
        reference_range_collection_name: Optional[str] = None,
        formula_name: Optional[str] = None,
        percent_drop_threshold: Optional[float] = None,
        calling_crf: Optional[Any] = None,
        subject_visit: Optional[Any] = None,
        assay_datetime: Optional[datetime] = None,
        egfr_drop_notification_model: Optional[str] = None,
    ):
        self._egfr_value: Optional[float] = None
        self._egfr_grade = None
        self._egfr_drop_value = None
        self._egfr_drop_grade = None
        self.assay_date = None
        self.subject_visit = None

        if formula_name not in self.calculators:
            raise EgfrError(
                f"Invalid formula_name. Expected one of {list(self.calculators.keys())}. "
                f"Got {formula_name}."
            )
        else:
            self.calculator_cls = self.calculators.get(formula_name)
        self.baseline_egfr_value = baseline_egfr_value
        self.age_in_years = age_in_years
        self.dob = dob
        self.egfr_drop_notification_model = egfr_drop_notification_model
        self.egfr_drop_units = PERCENT
        self.egfr_units = EGFR_UNITS
        self.ethnicity = ethnicity
        self.gender = gender
        self.reference_range_collection_name = reference_range_collection_name
        self.report_datetime = report_datetime

        if self.dob:
            self.age_in_years = age(born=self.dob, reference_dt=self.report_datetime).years
        elif self.age_in_years:
            self.dob = self.report_datetime - relativedelta(years=self.age_in_years)
        else:
            raise EgfrError("Expected `age_in_years` or `dob`. Got None for both.")

        if calling_crf:
            self.creatinine_units = calling_crf.creatinine_units
            self.creatinine_value = calling_crf.creatinine_value
            self.percent_drop_threshold = calling_crf.percent_drop_threshold
            self.subject_visit = calling_crf.subject_visit
            self.report_datetime = calling_crf.report_datetime
            self.assay_date = calling_crf.assay_datetime.astimezone(ZoneInfo("UTC")).date()
        else:
            self.creatinine_units = creatinine_units
            self.creatinine_value = creatinine_value
            self.percent_drop_threshold = percent_drop_threshold
            self.subject_visit = subject_visit
            if assay_datetime:
                self.assay_date = assay_datetime.astimezone(ZoneInfo("UTC")).date()

        if self.percent_drop_threshold is not None and self.percent_drop_threshold < 1:
            raise EgfrError(
                "Attr `percent_drop_threshold` should be a percentage. "
                f"Got {self.percent_drop_threshold}"
            )

        if self.egfr_drop_value and self.percent_drop_threshold is not None:
            if self.egfr_drop_value >= percent_drop_threshold:
                self.create_or_update_egfr_drop_notification()

    @property
    def egfr_value(self) -> float:
        if self._egfr_value is None:
            self._egfr_value = self.calculator_cls(
                gender=self.gender,
                ethnicity=self.ethnicity,
                age_in_years=self.age_in_years,
                creatinine_value=self.creatinine_value,
                creatinine_units=self.creatinine_units,
            ).value
        return self._egfr_value

    @property
    def egfr_grade(self) -> Optional[int]:
        if self._egfr_grade is None:
            reference_grp = site_reportables.get(self.reference_range_collection_name).get(
                "egfr"
            )
            grade_obj = reference_grp.get_grade(
                self.egfr_value,
                gender=self.gender,
                dob=self.dob,
                report_datetime=self.report_datetime,
                units=self.egfr_units,
            )
            if grade_obj:
                self._egfr_grade = grade_obj.grade
        return self._egfr_grade

    @property
    def egfr_drop_value(self) -> float:
        if self._egfr_drop_value is None:
            if self.baseline_egfr_value:
                egfr_drop_value = egfr_percent_change(
                    float(self.egfr_value), float(self.baseline_egfr_value)
                )
            else:
                egfr_drop_value = 0.0
            self._egfr_drop_value = 0.0 if egfr_drop_value < 0.0 else egfr_drop_value
        return self._egfr_drop_value

    @property
    def egfr_drop_grade(self) -> Optional[int]:
        if self._egfr_drop_grade is None:
            reference_grp = site_reportables.get(self.reference_range_collection_name).get(
                "egfr_drop"
            )
            grade_obj = reference_grp.get_grade(
                self.egfr_drop_value,
                gender=self.gender,
                dob=self.dob,
                report_datetime=self.report_datetime,
                units=self.egfr_drop_units,
            )
            if grade_obj:
                self._egfr_drop_grade = grade_obj.grade
        return self._egfr_drop_grade

    def create_or_update_egfr_drop_notification(self):
        """Creates or updates the `eGFR notification model`"""
        with transaction.atomic():
            try:
                obj = self.egfr_drop_notification_model_cls.objects.get(
                    subject_visit=self.subject_visit
                )
            except ObjectDoesNotExist:
                obj = self.egfr_drop_notification_model_cls.objects.create(
                    subject_visit=self.subject_visit,
                    report_datetime=self.report_datetime,
                    creatinine_date=self.assay_date,
                    egfr_percent_change=self.egfr_drop_value,
                    report_status=NEW,
                    consent_version=self.subject_visit.consent_version,
                )
            else:
                obj.egfr_percent_change = self.egfr_drop_value
                obj.creatinine_date = self.assay_date
                obj.save()
        obj.refresh_from_db()
        return obj

    @property
    def egfr_drop_notification_model_cls(self):
        return get_egfr_drop_notification_model_cls()
