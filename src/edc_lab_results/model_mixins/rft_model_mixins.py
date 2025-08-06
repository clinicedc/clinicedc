from django.db import models
from edc_lab_panel.model_mixin_factory import reportable_result_model_mixin_factory
from edc_reportable.units import (
    MICROMOLES_PER_LITER,
    MICROMOLES_PER_LITER_DISPLAY,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    MILLIMOLES_PER_LITER_DISPLAY,
)


class CreatinineModelMixin(
    reportable_result_model_mixin_factory(
        utest_id="creatinine",
        verbose_name="Creatinine",
        units_choices=(
            (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
            (MICROMOLES_PER_LITER, MICROMOLES_PER_LITER_DISPLAY),
        ),
    ),
    models.Model,
):
    class Meta:
        abstract = True


class UreaModelMixin(
    reportable_result_model_mixin_factory(
        utest_id="urea",
        verbose_name="Urea (BUN)",
        units_choices=((MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),),
    ),
    models.Model,
):
    class Meta:
        abstract = True


class UricAcidModelMixin(
    reportable_result_model_mixin_factory(
        utest_id="uric_acid",
        verbose_name="Uric Acid",
        decimal_places=4,
        max_digits=10,
        units_choices=(
            (MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
            (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
        ),
    ),
    models.Model,
):
    class Meta:
        abstract = True
