from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from edc_lab_panel.constants import (
    HAEMOGLOBIN,
    HCT,
    LYMPHOCYTE,
    LYMPHOCYTE_DIFF,
    MCH,
    MCHC,
    MCV,
    NEUTROPHIL,
    NEUTROPHIL_DIFF,
    PLATELETS,
    RBC,
    WBC,
)
from edc_reportable import GRAMS_PER_DECILITER, PERCENT
from edc_reportable.units import (
    CELLS_PER_MILLIMETER_CUBED,
    CELLS_PER_MILLIMETER_CUBED_DISPLAY,
    FEMTOLITERS_PER_CELL,
    PICOGRAMS_PER_CELL,
    TEN_X_9_PER_LITER,
)

from ..model_mixin_factories import reportable_result_model_mixin_factory


class HaemoglobinModelMixin(
    reportable_result_model_mixin_factory(
        utest_id=HAEMOGLOBIN,
        verbose_name="Haemoglobin",
        units_choices=((GRAMS_PER_DECILITER, GRAMS_PER_DECILITER),),
        decimal_places=1,
    ),
    models.Model,
):
    class Meta:
        abstract = True


class HctModelMixin(
    reportable_result_model_mixin_factory(
        utest_id=HCT,
        verbose_name="Hematocrit",
        units_choices=((PERCENT, PERCENT),),
        validators=[MinValueValidator(1.0), MaxValueValidator(999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class MchModelMixin(
    reportable_result_model_mixin_factory(
        utest_id=MCH,
        units_choices=((PICOGRAMS_PER_CELL, PICOGRAMS_PER_CELL),),
    ),
    models.Model,
):
    class Meta:
        abstract = True


class MchcModelMixin(
    reportable_result_model_mixin_factory(
        utest_id=MCHC,
        units_choices=((GRAMS_PER_DECILITER, GRAMS_PER_DECILITER),),
    ),
    models.Model,
):
    class Meta:
        abstract = True


class McvModelMixin(
    reportable_result_model_mixin_factory(
        utest_id=MCV,
        units_choices=((FEMTOLITERS_PER_CELL, FEMTOLITERS_PER_CELL),),
    ),
    models.Model,
):
    class Meta:
        abstract = True


class NeutrophilModelMixin(
    reportable_result_model_mixin_factory(
        utest_id=NEUTROPHIL,
        verbose_name="Neutrophil (abs)",
        units_choices=((TEN_X_9_PER_LITER, TEN_X_9_PER_LITER),),
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(9999)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class NeutrophilDiffModelMixin(
    reportable_result_model_mixin_factory(
        utest_id=NEUTROPHIL_DIFF,
        verbose_name="Neutrophil (diff)",
        units_choices=((PERCENT, PERCENT),),
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(9999)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class LymphocyteModelMixin(
    reportable_result_model_mixin_factory(
        utest_id=LYMPHOCYTE,
        verbose_name="Lymphocyte (abs)",
        units_choices=((TEN_X_9_PER_LITER, TEN_X_9_PER_LITER),),
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(9999)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class LymphocyteDiffModelMixin(
    reportable_result_model_mixin_factory(
        utest_id=LYMPHOCYTE_DIFF,
        verbose_name="Lymphocyte (diff)",
        units_choices=((PERCENT, PERCENT),),
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(9999)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class PlateletsModelMixin(
    reportable_result_model_mixin_factory(
        utest_id=PLATELETS,
        verbose_name="Platelets",
        units_choices=(
            (TEN_X_9_PER_LITER, TEN_X_9_PER_LITER),
            (CELLS_PER_MILLIMETER_CUBED, CELLS_PER_MILLIMETER_CUBED_DISPLAY),
        ),
        decimal_places=0,
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class RbcModelMixin(
    reportable_result_model_mixin_factory(
        utest_id=RBC,
        verbose_name="Red blood cell count",
        units_choices=(
            (TEN_X_9_PER_LITER, TEN_X_9_PER_LITER),
            (CELLS_PER_MILLIMETER_CUBED, CELLS_PER_MILLIMETER_CUBED),
        ),
        validators=[MinValueValidator(1.0), MaxValueValidator(999999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class WbcModelMixin(
    reportable_result_model_mixin_factory(
        utest_id=WBC,
        units_choices=(
            (TEN_X_9_PER_LITER, TEN_X_9_PER_LITER),
            (CELLS_PER_MILLIMETER_CUBED, CELLS_PER_MILLIMETER_CUBED_DISPLAY),
        ),
    ),
    models.Model,
):
    class Meta:
        abstract = True
