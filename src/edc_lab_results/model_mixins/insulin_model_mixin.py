from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_glucose.model_mixins import fasting_model_mixin_factory
from edc_lab_panel.model_mixin_factory import reportable_result_model_mixin_factory
from edc_reportable.units import MICRO_IU_MILLILITER, MICRO_IU_MILLILITER_DISPLAY


class BaseInsulinModelMixin(
    reportable_result_model_mixin_factory(
        utest_id="ins",
        verbose_name="Insulin",
        units_choices=((MICRO_IU_MILLILITER, MICRO_IU_MILLILITER_DISPLAY),),
        validators=[MinValueValidator(0.0), MaxValueValidator(999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class InsulinModelMixin(BaseInsulinModelMixin, fasting_model_mixin_factory(), models.Model):
    class Meta:
        abstract = True
