from gettext import gettext as _

from django import forms

from ..calculators import CalculatorError, calculate_bmi


class WeightHeightBmiFormValidatorMixin:
    @staticmethod
    def validate_weight_height_with_bmi(weight_kg=None, height_cm=None, **kwargs):
        try:
            bmi = calculate_bmi(weight_kg=weight_kg, height_cm=height_cm, **kwargs)
        except CalculatorError as err:
            errmsg = _("Please check weight and height. {err}").format(err=err)
            raise forms.ValidationError(errmsg) from err
        return bmi
