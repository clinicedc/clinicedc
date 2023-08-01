from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from edc_constants.constants import NEW
from edc_reportable import site_reportables
from edc_reportable.units import EGFR_UNITS, PERCENT
from edc_utils import age, get_utcnow

from .calculators import EgfrCkdEpi, EgfrCockcroftGault, egfr_percent_change
from .get_drop_notification_model import get_egfr_drop_notification_model_cls

if TYPE_CHECKING:
    from edc_visit_tracking.typing_stubs import RelatedVisitProtocol


class EgfrError(Exception):
    pass


class Egfr:
    calculators: dict = {"ckd-epi": EgfrCkdEpi, "cockcroft-gault": EgfrCockcroftGault}

    def __init__(
        self,
        baseline_egfr_value: Decimal | float | None = None,
        gender: str | None = None,
        ethnicity: str | None = None,
        age_in_years: int | None = None,
        dob: date | None = None,
        weight_in_kgs: Decimal | float | None = None,
        report_datetime: datetime | None = None,
        creatinine_value: Decimal | float | None = None,
        creatinine_units: str | None = None,
        formula_name: str | None = None,
        value_threshold: Decimal | float | None = None,
        percent_drop_threshold: Decimal | float | None = None,
        reference_range_collection_name: str | None = None,
        calling_crf: Any | None = None,
        related_visit: RelatedVisitProtocol | None = None,
        assay_datetime: datetime | None = None,
        egfr_drop_notification_model: str | None = None,
    ):
        self._egfr_value: Decimal | None = None
        self._egfr_grade = None
        self._egfr_drop_value: Decimal | None = None
        self._egfr_drop_grade = None
        self.assay_date: date | None = None
        self.related_visit = None

        self.baseline_egfr_value = baseline_egfr_value
        if formula_name not in self.calculators:
            raise EgfrError(
                f"Invalid formula_name. Expected one of {list(self.calculators.keys())}. "
                f"Got {formula_name}."
            )
        else:
            self.calculator_cls = self.calculators.get(formula_name)
        self.age_in_years = age_in_years
        self.dob = dob
        self.weight_in_kgs = weight_in_kgs
        self.egfr_drop_notification_model = egfr_drop_notification_model
        self.egfr_drop_units = PERCENT
        self.egfr_units = EGFR_UNITS
        self.ethnicity = ethnicity
        self.gender = gender
        self.reference_range_collection_name = reference_range_collection_name
        self.report_datetime = report_datetime
        self.value_threshold = value_threshold
        self.percent_drop_threshold = percent_drop_threshold

        if self.dob:
            self.age_in_years = age(
                born=self.dob, reference_dt=self.report_datetime.astimezone(ZoneInfo("UTC"))
            ).years
        elif not self.dob and self.age_in_years:
            self.dob = (
                self.report_datetime.astimezone(ZoneInfo("UTC"))
                - relativedelta(years=self.age_in_years)
            ).date()
        else:
            raise EgfrError("Expected `age_in_years` or `dob`. Got None for both.")

        if calling_crf:
            self.creatinine_units = calling_crf.creatinine_units
            self.creatinine_value = calling_crf.creatinine_value
            self.percent_drop_threshold = calling_crf.percent_drop_threshold
            self.related_visit = calling_crf.related_visit
            self.report_datetime = calling_crf.report_datetime
            self.assay_date = calling_crf.assay_datetime.astimezone(ZoneInfo("UTC")).date()
        else:
            self.creatinine_units = creatinine_units
            self.creatinine_value = creatinine_value
            self.percent_drop_threshold = percent_drop_threshold
            self.related_visit = related_visit
            self.report_datetime = report_datetime
            if assay_datetime:
                self.assay_date = assay_datetime.astimezone(ZoneInfo("UTC")).date()

        if self.percent_drop_threshold is not None and self.percent_drop_threshold < 1.0:
            raise EgfrError(
                "Attr `percent_drop_threshold` should be a percentage. "
                f"Got {self.percent_drop_threshold}"
            )

        self.on_value_threshold_reached()

        self.on_percent_drop_threshold_reached()

    def on_value_threshold_reached(self) -> None:
        """A hook to respond if egfr value is at or beyond the value
        threshold.
        """
        pass

    def on_percent_drop_threshold_reached(self) -> None:
        """A hook to respond if egfr percent drop from baseline
        is at or beyond the percent drop threshold.
        """
        if self.egfr_drop_value and self.percent_drop_threshold is not None:
            if self.egfr_drop_value >= self.percent_drop_threshold:
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
                weight=self.get_weight_in_kgs(),
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
                egfr_drop_value = 0.0000
            self._egfr_drop_value = 0.0000 if egfr_drop_value < 0.0000 else egfr_drop_value
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

    def get_weight_in_kgs(self) -> Optional[float]:
        return self.weight_in_kgs

    def create_or_update_egfr_drop_notification(self):
        """Creates or updates the `eGFR notification model`"""
        with transaction.atomic():
            try:
                obj = self.egfr_drop_notification_model_cls.objects.get(
                    subject_visit__id=self.related_visit.id
                )
            except ObjectDoesNotExist:
                obj = self.egfr_drop_notification_model_cls.objects.create(
                    subject_visit_id=self.related_visit.id,
                    report_datetime=self.report_datetime,
                    egfr_value=self.egfr_value,
                    creatinine_date=self.assay_date,
                    creatinine_value=self.creatinine_value,
                    creatinine_units=self.creatinine_units,
                    weight=self.get_weight_in_kgs(),
                    egfr_percent_change=self.egfr_drop_value,
                    report_status=NEW,
                    site_id=self.related_visit.site.id,
                )
            else:
                obj.egfr_value = self.egfr_value
                obj.creatinine_value = self.creatinine_value
                obj.weight = self.get_weight_in_kgs()
                obj.egfr_percent_change = self.egfr_drop_value
                obj.creatinine_date = self.assay_date
                obj.modified = get_utcnow()
                obj.save()
        obj.refresh_from_db()
        return obj

    @property
    def egfr_drop_notification_model_cls(self):
        return get_egfr_drop_notification_model_cls()
