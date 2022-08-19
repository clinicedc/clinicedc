from django.db import models
from django.utils.html import format_html
from edc_constants.constants import NOT_APPLICABLE
from edc_lab.choices import GLUCOSE_UNITS_NA, RESULT_QUANTIFIER
from edc_lab.constants import EQ
from edc_model.validators import datetime_not_future

from ..constants import GLUCOSE_HIGH_READING


def ogtt_model_mixin_factory(utest_id: str, **kwargs):
    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    opts = {
        f"{utest_id}_base_datetime": models.DateTimeField(
            verbose_name="Date/time oral glucose solution given",
            validators=[datetime_not_future],
            null=True,
            blank=True,
            help_text="(glucose solution given)",
        ),
        f"{utest_id}_value": models.DecimalField(
            verbose_name=format_html(
                "Blood glucose measure 2hrs <u>after</u> oral glucose solution given"
            ),
            max_digits=8,
            decimal_places=2,
            null=True,
            blank=True,
            help_text=f"A `HIGH` reading may be entered as {GLUCOSE_HIGH_READING}",
        ),
        f"{utest_id}_quantifier": models.CharField(
            max_length=10,
            choices=RESULT_QUANTIFIER,
            default=EQ,
        ),
        f"{utest_id}_units": models.CharField(
            verbose_name="Units (Blood glucose 2hrs after...)",
            max_length=15,
            default=NOT_APPLICABLE,
            choices=GLUCOSE_UNITS_NA,
            blank=False,
        ),
        f"{utest_id}_datetime": models.DateTimeField(
            verbose_name=format_html(
                "Date/time blood glucose measured 2hrs <u>after</u> "
                "oral glucose solution given"
            ),
            validators=[datetime_not_future],
            blank=True,
            null=True,
            help_text="(2 hours after glucose solution given)",
        ),
    }

    opts.update(**kwargs)

    for name, fld_cls in opts.items():
        AbstractModel.add_to_class(name, fld_cls)

    return AbstractModel


class OgttModelMixin(ogtt_model_mixin_factory("ogtt"), models.Model):
    """A model mixin of fields for the OGTT"""

    class Meta:
        abstract = True
