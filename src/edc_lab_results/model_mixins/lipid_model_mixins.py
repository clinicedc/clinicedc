from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_lab_panel.model_mixin_factory import reportable_result_model_mixin_factory
from edc_reportable.units import MILLIMOLES_PER_LITER


class CholModelMixin(
    reportable_result_model_mixin_factory(
        utest_id="chol",
        verbose_name="Total Cholesterol",
        decimal_places=2,
        max_digits=8,
        units_choices=((MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER),),
        validators=[MinValueValidator(0.00), MaxValueValidator(999.00)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class HdlModelMixin(
    reportable_result_model_mixin_factory(
        utest_id="hdl",
        decimal_places=2,
        max_digits=8,
        units_choices=((MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER),),
        validators=[MinValueValidator(0.00), MaxValueValidator(999.00)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class LdlModelMixin(
    reportable_result_model_mixin_factory(
        utest_id="ldl",
        decimal_places=2,
        max_digits=8,
        units_choices=((MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER),),
        validators=[MinValueValidator(0.00), MaxValueValidator(999.00)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class TrigModelMixin(
    reportable_result_model_mixin_factory(
        utest_id="trig",
        decimal_places=2,
        max_digits=8,
        units_choices=((MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER),),
        validators=[MinValueValidator(0.00), MaxValueValidator(999.00)],
        verbose_name="Triglycerides",
    ),
    models.Model,
):
    class Meta:
        abstract = True
