from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from edc_lab_panel.model_mixin_factory import reportable_result_model_mixin_factory
from edc_registration.models import RegisteredSubject
from edc_reportable import PERCENT

from ..egfr import Egfr


class EgfrDropModelMixin(
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
    """Declared with a bloodresult RFT CRF model"""

    percent_drop_threshold: Optional[float] = 20
    baseline_timepoint: Optional[int] = 0
    egfr_formula_name: Optional[str] = None

    def save(self, *args, **kwargs):
        rs = RegisteredSubject.objects.get(
            subject_identifier=self.subject_visit.subject_identifier
        )
        egfr = Egfr(
            calling_crf=self,
            dob=rs.dob,
            gender=rs.gender,
            percent_drop_threshold=self.percent_drop_threshold,
            report_datetime=self.report_datetime,
            baseline_egfr_value=self.get_baseline_egfr_value(),
            formula_name=self.egfr_formula_name,
            reference_range_collection_name=self.get_reference_range_collection_name(),
        )
        self.egfr_value = egfr.egfr_value
        self.egfr_units = egfr.egfr_units
        self.egfr_grade = egfr.egfr_grade
        self.egfr_drop_value = egfr.egfr_drop_value
        self.egfr_drop_units = egfr.egfr_drop_units
        self.egfr_drop_grade = egfr.egfr_drop_grade
        super().save(*args, **kwargs)

    def get_baseline_egfr_value(
        self, subject_visit=None, baseline_timepoint=None
    ) -> Optional[float]:
        egfr_value = None
        baseline_timepoint = (
            self.baseline_timepoint if baseline_timepoint is None else baseline_timepoint
        )
        if not subject_visit:
            with transaction.atomic():
                try:
                    subject_visit = self.subject_visit.__class__.objects.get(
                        appointment__timepoint=baseline_timepoint,
                        visit_code_sequence=0,
                    )
                except ObjectDoesNotExist:
                    pass
        if subject_visit:
            with transaction.atomic():
                try:
                    egfr_value = self.__class__.objects.get(
                        subject_visit=subject_visit
                    ).egfr_value
                except ObjectDoesNotExist:
                    pass
        return egfr_value

    class Meta:
        abstract = True
