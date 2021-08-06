from django import forms
from edc_constants.constants import YES

from ..utils import calculate_avg_bp, has_severe_htn


class BloodPressureFormValidatorMixin:
    """Coupled with BloodPressureModelMixin"""

    @staticmethod
    def raise_on_avg_blood_pressure_suggests_severe_htn(
        use_avg=None, severe_htn_field_name=None, errmsg=None, **kwargs
    ):
        """Raise if BP is >= 180/120"""
        severe_htn_field_name = severe_htn_field_name or "severe_htn"
        severe_htn_reponse = kwargs.get(severe_htn_field_name)
        errmsg = {
            severe_htn_field_name: (errmsg or "Invalid. Patient has severe hypertension")
        }
        use_avg = True if use_avg is None else False
        avg_sys, avg_dia = calculate_avg_bp(use_av=use_avg, **kwargs)
        if has_severe_htn(sys=avg_sys, dia=avg_dia):
            if severe_htn_reponse != YES:
                raise forms.ValidationError(errmsg)
