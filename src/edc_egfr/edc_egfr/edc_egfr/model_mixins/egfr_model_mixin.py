from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from edc_lab_panel.model_mixin_factory import reportable_result_model_mixin_factory
from edc_registration.models import RegisteredSubject
from edc_reportable.units import EGFR_UNITS, PERCENT
from edc_reportable.utils import get_reference_range_collection_name

from ..calculators import EgfrCalculatorError
from ..egfr import Egfr


class EgfrModelMixin(
    reportable_result_model_mixin_factory(
        utest_id="egfr",
        verbose_name="eGFR",
        decimal_places=4,
        default_units=EGFR_UNITS,
        max_digits=8,
        units_choices=((EGFR_UNITS, EGFR_UNITS),),
    ),
    reportable_result_model_mixin_factory(
        utest_id="egfr_drop",
        verbose_name="eGFR Drop",
        decimal_places=4,
        default_units=PERCENT,
        max_digits=10,
        units_choices=((PERCENT, PERCENT),),
    ),
    models.Model,
):

    """Declared with a bloodresult RFT CRF model.

    As a lab result CRF, expects subject_visit, requisition
    and report_datetime.

    See edc_lab_result, edc_crf.
    """

    percent_drop_threshold: float = 20.0
    baseline_timepoint: int = 0
    egfr_formula_name: str = None
    egfr_cls = Egfr

    def save(self, *args, **kwargs):
        self.set_egfr_value_or_raise()
        super().save(*args, **kwargs)

    def set_egfr_value_or_raise(self) -> None:
        egfr = self.egfr_cls(**self.egfr_options)
        try:
            self.egfr_value = egfr.egfr_value
        except EgfrCalculatorError:
            if self.creatinine_value:
                raise
            self.egfr_value = None
            self.egfr_units = None
            self.egfr_grade = None
            self.egfr_drop_value = None
            self.egfr_drop_units = None
            self.egfr_drop_grade = None
        else:
            self.egfr_units = egfr.egfr_units
            self.egfr_grade = egfr.egfr_grade
            self.egfr_drop_value = egfr.egfr_drop_value
            self.egfr_drop_units = egfr.egfr_drop_units
            self.egfr_drop_grade = egfr.egfr_drop_grade

    @property
    def egfr_options(self) -> dict:
        rs = RegisteredSubject.objects.get(
            subject_identifier=self.related_visit.subject_identifier
        )
        return dict(
            calling_crf=self,
            dob=rs.dob,
            gender=rs.gender,
            ethnicity=rs.ethnicity,
            weight_in_kgs=self.get_weight_in_kgs_for_egfr(),
            percent_drop_threshold=self.percent_drop_threshold,
            value_threshold=45.0000,
            report_datetime=self.report_datetime,
            baseline_egfr_value=self.get_baseline_egfr_value(),
            formula_name=self.egfr_formula_name,
            reference_range_collection_name=get_reference_range_collection_name(self),
        )

    def get_baseline_egfr_value(self) -> float | None:
        """Returns a baseline or reference eGFR value.

        Expects a longitudinal / CRF model with attrs `subject_visit`.
        """
        egfr_value = None
        with transaction.atomic():
            baseline_visit = self.related_visit.__class__.objects.get(
                appointment__subject_identifier=self.related_visit.subject_identifier,
                appointment__visit_schedule_name=self.related_visit.visit_schedule_name,
                appointment__schedule_name=self.related_visit.schedule_name,
                appointment__timepoint=self.baseline_timepoint,
                visit_code_sequence=0,
            )
        with transaction.atomic():
            try:
                egfr_value = self.__class__.objects.get(
                    subject_visit=baseline_visit
                ).egfr_value
            except ObjectDoesNotExist:
                pass
        return egfr_value

    def get_weight_in_kgs_for_egfr(self) -> Decimal | None:
        return None

    class Meta:
        abstract = True
