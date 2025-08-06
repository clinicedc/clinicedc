from django.db import models
from edc_lab_panel.model_mixin_factory import reportable_result_model_mixin_factory
from edc_reportable.units import PLUS


class ProteinuriaModelMixin(
    reportable_result_model_mixin_factory(
        utest_id="proteinuria",
        verbose_name="Proteinuria",
        units_choices=((PLUS, PLUS),),
        decimal_places=1,
    ),
    models.Model,
):
    class Meta:
        abstract = True
