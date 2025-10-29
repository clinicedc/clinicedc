from clinicedc_constants import PLUS
from django.db import models

from ..model_mixin_factories import reportable_result_model_mixin_factory


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
