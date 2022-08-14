from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional, Union
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
        calculator_name: Optional[str] = None,
        notify_on_percent_drop: Optional[float] = None,
        calling_crf: Optional[Any] = None,
        egfr_drop_notification_model: Optional[str] = None,
    ):
        self._egfr_value: Optional[float] = None
        self._egfr_grade = None
        self._egfr_drop_value = None
        self._egfr_drop_grade = None

        if calculator_name not in self.calculators:
            raise EgfrError(
                f"Invalid calculator name. Expected one of {list(self.calculators.keys())}. "
                f"Got {calculator_name}."
            )
        else:
            self.calculator_cls = self.calculators.get(calculator_name)
        self.baseline_egfr_value = baseline_egfr_value
        self.age_in_years = age_in_years
        self.dob = dob
        self.calling_crf = calling_crf
        self.creatinine_units = creatinine_units
        self.creatinine_value = creatinine_value
        self.egfr_drop_notification_model = egfr_drop_notification_model
        self.egfr_drop_units = PERCENT
        self.egfr_units = EGFR_UNITS
        self.ethnicity = ethnicity
        self.gender = gender
        self.reference_range_collection_name = reference_range_collection_name
        self.report_datetime = report_datetime

        if self.dob:
            self.age_in_years = age(born=self.dob, reference_dt=self.report_datetime).years
        else:
            self.dob = self.report_datetime - relativedelta(years=self.age_in_years)
        if self.egfr_drop_value and notify_on_percent_drop is not None:
            if self.egfr_drop_value >= notify_on_percent_drop:
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
                    subject_visit=self.calling_crf.subject_visit
                )
            except ObjectDoesNotExist:
                obj = self.egfr_drop_notification_model_cls.objects.create(
                    subject_visit=self.calling_crf.subject_visit,
                    report_datetime=self.calling_crf.report_datetime,
                    creatinine_date=self.calling_crf.assay_datetime.date(),
                    egfr_percent_change=self.egfr_drop_value,
                    report_status=NEW,
                    consent_version=self.calling_crf.subject_visit.consent_version,
                )
            else:
                obj.egfr_percent_change = self.egfr_drop_value
                obj.creatinine_date = self.calling_crf.assay_datetime.astimezone(
                    ZoneInfo("UTC")
                ).date()
                obj.save()
        obj.refresh_from_db()
        return obj

    @property
    def egfr_drop_notification_model_cls(self):
        return get_egfr_drop_notification_model_cls()
