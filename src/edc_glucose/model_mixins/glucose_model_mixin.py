from __future__ import annotations

from django.db import models
from edc_constants.constants import NOT_APPLICABLE
from edc_lab.choices import GLUCOSE_UNITS_NA, RESULT_QUANTIFIER_NA

from ..constants import GLUCOSE_HIGH_READING
from . import fasting_model_mixin_factory


def glucose_model_mixin_factory(utest_id: str, verbose_names: dict | None = None, **kwargs):
    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    opts = {
        f"{utest_id}_value": models.DecimalField(
            verbose_name="Glucose level",
            max_digits=8,
            decimal_places=2,
            null=True,
            blank=True,
            help_text=f"A `HIGH` reading may be entered as {GLUCOSE_HIGH_READING}",
        ),
        f"{utest_id}_quantifier": models.CharField(
            verbose_name="Glucose quantifier",
            max_length=10,
            choices=RESULT_QUANTIFIER_NA,
            default=NOT_APPLICABLE,
        ),
        f"{utest_id}_units": models.CharField(
            verbose_name="Glucose units",
            max_length=15,
            choices=GLUCOSE_UNITS_NA,
            default=NOT_APPLICABLE,
        ),
        f"{utest_id}_date": models.DateField(
            verbose_name="Glucose date measured",
            null=True,
            blank=True,
        ),
    }

    opts.update(**kwargs)

    for name, fld_cls in opts.items():
        AbstractModel.add_to_class(name, fld_cls)

    return AbstractModel


class GlucoseModelMixin(
    glucose_model_mixin_factory("glucose"),
    fasting_model_mixin_factory("glucose"),
    models.Model,
):
    """A model mixin of fields for the Glucose, fasting or random"""

    class Meta:
        abstract = True
