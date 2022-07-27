from typing import Optional

from django.core.validators import MinValueValidator
from django.db import models
from edc_constants.choices import GRADING_SCALE_WITH_NOT_GRADED, YES_NO
from edc_lab.choices import RESULT_QUANTIFIER
from edc_lab.constants import EQ
from edc_reportable.choices import REPORTABLE


def get_field_attrs_for_utestid(
    utest_id: str,
    units_choices: tuple,
    default_units: Optional[str] = None,
    verbose_name: Optional[str] = None,
    decimal_places: Optional[int] = None,
    max_digits: Optional[int] = None,
    validators: Optional[list] = None,
    quantifier: Optional[list] = None,
    help_text: Optional[list] = None,
) -> dict:
    """Returns a dictionary of field classes for the model"""
    value_options = dict(
        verbose_name=verbose_name or utest_id.upper(),
        decimal_places=decimal_places or 2,
        max_digits=max_digits or 8,
        validators=validators or [MinValueValidator(0.00)],
        null=True,
        blank=True,
    )
    if help_text:
        value_options.update(help_text=help_text)
    units_options = dict(
        verbose_name="units",
        max_length=15,
        choices=units_choices,
        null=True,
        blank=True,
    )
    if default_units:
        units_options.update(default=default_units)

    quantifier_options = dict(
        verbose_name="Quantifier",
        max_length=10,
        choices=RESULT_QUANTIFIER,
        default=EQ,
        null=True,
        blank=True,
    )
    return {
        f"{utest_id}_value": models.DecimalField(**value_options),
        f"{utest_id}_units": models.CharField(**units_options),
        f"{utest_id}_quantifier": models.CharField(**quantifier_options),
    }


def get_field_attrs_for_reportable(utest_id: str) -> dict:
    """Returns a dictionary of field classes for the model"""
    return {
        f"{utest_id}_abnormal": models.CharField(
            verbose_name="abnormal", choices=YES_NO, max_length=25, null=True, blank=True
        ),
        f"{utest_id}_reportable": models.CharField(
            verbose_name="reportable",
            choices=REPORTABLE,
            max_length=25,
            null=True,
            blank=True,
        ),
        f"{utest_id}_grade": models.IntegerField(
            verbose_name="Grade",
            choices=GRADING_SCALE_WITH_NOT_GRADED,
            null=True,
            blank=True,
        ),
        f"{utest_id}_grade_description": models.CharField(
            verbose_name="Grade description",
            max_length=250,
            null=True,
            blank=True,
        ),
    }
