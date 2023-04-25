from __future__ import annotations

from django.db import models
from edc_constants.choices import YES_NO_NA
from edc_constants.constants import NOT_APPLICABLE
from edc_model.validators import hm_validator


def fasting_model_mixin_factory(
    prefix: str = None, verbose_names: dict | None = None, **kwargs
):
    prefix = "" if prefix is None else f"{prefix}_"
    verbose_names = verbose_names or {}

    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    opts = {
        f"{prefix}fasting": models.CharField(
            verbose_name=verbose_names.get(f"{prefix}fasting", "Has the participant fasted?"),
            max_length=15,
            choices=YES_NO_NA,
            default=NOT_APPLICABLE,
            blank=False,
            help_text="As reported by patient",
        ),
        f"{prefix}fasting_duration_str": models.CharField(
            verbose_name=verbose_names.get(
                f"{prefix}fasting_duration_str",
                "How long have they fasted in hours and/or minutes?",
            ),
            max_length=8,
            validators=[hm_validator],
            null=True,
            blank=True,
            help_text=(
                "As reported by patient. Duration of fast. Format is `HHhMMm`. "
                "For example 1h23m, 12h7m, etc"
            ),
        ),
        f"{prefix}fasting_duration_minutes": models.IntegerField(
            null=True, help_text="system calculated value"
        ),
    }

    opts.update(**kwargs)

    for name, fld_cls in opts.items():
        AbstractModel.add_to_class(name, fld_cls)

    return AbstractModel


class FastingModelMixin(fasting_model_mixin_factory(), models.Model):
    """A model mixin of fields about fasting.

    Used together with mixins for glucose measurements.
    """

    class Meta:
        abstract = True
