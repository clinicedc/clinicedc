from django.db import models
from edc_lab_panel.model_mixin_factory import reportable_result_model_mixin_factory
from edc_reportable.units import EGFR_UNITS


class EgfrModelMixin(
    reportable_result_model_mixin_factory(
        utest_id="egfr",
        verbose_name="eGFR",
        decimal_places=4,
        default_units=EGFR_UNITS,
        max_digits=8,
        units_choices=((EGFR_UNITS, EGFR_UNITS),),
    ),
    models.Model,
):

    """Declared with a bloodresult RFT CRF model"""

    class Meta:
        abstract = True
