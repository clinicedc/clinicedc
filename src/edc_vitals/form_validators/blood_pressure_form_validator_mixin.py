from django import forms
from edc_constants.constants import YES

from ..utils import calculate_avg_bp, has_severe_htn


class BloodPressureFormValidatorMixin:
    """Coupled with BloodPressureModelMixin"""

    @staticmethod
    def raise_on_avg_blood_pressure_suggests_severe_htn(
        use_avg=None, severe_htn_field_name=None, errmsg=None, **kwargs
    ):
        """Raise if BP is >= 180/110, See settings"""
        severe_htn_field_name = severe_htn_field_name or "severe_htn"
        severe_htn_response = kwargs.get(severe_htn_field_name)
        errmsg = {
            severe_htn_field_name: (errmsg or "Invalid. Patient has severe hypertension")
        }
        use_avg = True if use_avg is None else False
        avg_sys, avg_dia = calculate_avg_bp(use_av=use_avg, **kwargs)
        if has_severe_htn(sys=avg_sys, dia=avg_dia):
            if severe_htn_response != YES:
                raise forms.ValidationError(errmsg)

    @staticmethod
    def raise_on_systolic_lt_diastolic_bp(
        sys_field: str = None, dia_field: str = None, **kwargs
    ) -> None:
        """Raise if systolic BP is < diastolic BP."""
        sys_field = sys_field or "sys_blood_pressure"
        dia_field = dia_field or "dia_blood_pressure"
        sys_response = kwargs.get(sys_field)
        dia_response = kwargs.get(dia_field)
        if sys_response and dia_response:
            if sys_response < dia_response:
                raise forms.ValidationError(
                    {dia_field: "Invalid. Diastolic must be less than systolic."}
                )
